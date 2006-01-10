#!/usr/bin/python

import glob, sqlite, sys, re, os, string
import darlib

htmldir = '/dar/tmp/html'

index_template = '''
<?_head('RPM packages for Red Hat / Fedora / Aurora')?>

<?_title('Alphabetic overview')?>
%(alphabeticlist)s

<?_title('Classified overview')?>
%(categorylist)s

<?_foot()?>
'''

category_template = '''
<?_head('RPM packages in group %(category)s')?>

%(packagelist)s

<?_foot()?>
'''

package_template = '''
<?_head('%(name)s RPM package for Red Hat / Fedora / Aurora')?>

<b>%(summary)s</b><br />
<pre>%(description)s</pre><br />

<small>
<b>Latest release:</b> %(version)s-%(release)s<br /><br />
<b>Website:</b> <a href="%(url)s">%(url)s</a><br />
<b>License:</b> %(license)s<br />
<b>Group:</b> <a href="../group-%(categoryidx)s.php">%(category)s</a><br />
<b>Maintainer:</b> <a href="/packager/persona/%(authority)s/">%(authority)s</a><br />
</small>

%(rpmlist)s
<?_foot()?>
'''

def convgroup(str):
	return str.translate(string.maketrans('/ ','-.')).lower()

sys.stdout = os.fdopen(1, 'w', 0)

con, cur = darlib.opendb()

try: os.mkdir(htmldir)
except: pass

# FIXME: Create the alphabetic list
categorylist = ''
alphabeticlist = 'TBD'

cur.execute('select distinct category from spec order by category')
for (category,) in cur.fetchall():
	print category
	# FIXME: Add license when rpmdb has been improved
	cur.execute('select name, version, release, authority, summary, description, category, url, license, parent, upstream from spec where category = "%s" order by name' % category)

	rec = {}
	packagelist = ''
	categorysize = 0
	for rec['name'], rec['version'], rec['release'], rec['authority'], rec['summary'], rec['description'], rec['category'], rec['url'], rec['license'], rec['parent'], rec['upstream'] in cur.fetchall():
		packagelist += '<a href="%(name)s/">%(name)s</a>: %(summary)s<br>\n' % rec
		
		try: os.mkdir(os.path.join(htmldir, rec['name']))
		except: pass

		# FIXME: Remove license when rpmdb has been improved and get authority fom specdb
		rec['categoryidx'] = convgroup(category)

		rec['rpmlist'] = '<h2>Package list (TBD)</h2> TBD'
#		cur.execute('select version, release, filename from pkg where parent = "%s" order by version' % rec['name'])
		cur.execute('select distinct filename from pkg where parent = "%s" order by version, filename' % rec['name'])

		for (filename, ) in cur.fetchall():
			rec['rpmlist'] += '  <div>%s</div>\n' % filename

		open(os.path.join(htmldir, rec['name'], 'index.php'), 'w').write(package_template % rec)

		categorysize+=1

	rec = { 'category': category, 'categoryidx': convgroup(category), 'categorysize': categorysize, 'packagelist': packagelist }
	categorylist += '<a href="group-%(categoryidx)s.php">%(category)s</a> (%(categorysize)s)<br>\n' % rec
	open(os.path.join(htmldir, 'group-' + convgroup(category)) + '.php', 'w').write(category_template % rec)

	# FIXME: Add alphabetic group files + index

rec = { 'categorylist': categorylist, 'alphabeticlist': 'alphabeticlist' }
open(os.path.join(htmldir, 'index.php'), 'w').write(index_template % rec)
