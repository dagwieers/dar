#!/usr/bin/python

import glob, sqlite, sys, re, os, string

htmldir = '/dar/tmp/html'
specdb = '/dar/tmp/state/specdb.sqlite'
infodb = '/dar/tmp/state/infodb.sqlite'

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
<b>Latest release:</b> #(version)s-#(release)s<br /><br />
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

infocon = sqlite.connect(infodb)
infocur = infocon.cursor()

infocur.execute('select distinct category from info order by category')

try: os.mkdir(htmldir)
except: pass

# FIXME: Create the alphabetic list
categorylist = ''
alphabeticlist = 'TBD'
for cat in infocur.fetchall():
	# FIXME: Add license when rpmdb has been improved
	infocur.execute('select name, summary, description, category, url, license, parent from info where category = "%s" order by name' % cat[0])

	rec = {}
	packagelist = ''
	categorysize = 0
	for rec['name'], rec['summary'], rec['description'], rec['category'], rec['url'], rec['url'], rec['parent'] in infocur.fetchall():
		packagelist += '<a href="%(name)s/">%(name)s</a>: %(summary)s<br>\n' % rec
		
		try: os.mkdir(os.path.join(htmldir, rec['name']))
		except: pass

		# FIXME: Remove license when rpmdb has been improved and get authority fom specdb
		rec['categoryidx'] = convgroup(cat[0])
		rec['authority'] = 'dag'
		rec['license'] = 'GPL'
		rec['rpmlist'] = '<h2>Package list (TBD)</h2> TBD'
		open(os.path.join(htmldir, rec['name'], 'index.php'), 'w').write(package_template % rec)

		categorysize+=1

	rec = { 'category': cat[0], 'categoryidx': convgroup(cat[0]), 'categorysize': categorysize, 'packagelist': packagelist }
	categorylist += '<a href="group-%(categoryidx)s.php">%(category)s</a> (%(categorysize)s)<br>\n' % rec
	open(os.path.join(htmldir, 'group-' + convgroup(cat[0])) + '.php', 'w').write(category_template % rec)

	# FIXME: Add alphabetic group files + index

rec = { 'categorylist': categorylist, 'alphabeticlist': 'alphabeticlist' }
open(os.path.join(htmldir, 'index.php'), 'w').write(index_template % rec)

infocur.close()
infocon.close()
