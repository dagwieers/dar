#!/usr/bin/python

import glob, sqlite, sys, re, os, string

htmldir = '/dar/tmp/html'
specdb = '/dar/tmp/state/specdb.sqlite'

headers = [ 'name', 'summary', 'description', 'authority', 'version', 'release', 'license', 'category', 'url' ]

category_template = '''
<?_head('RPM packages in group %(category)s')?>

#(packagelist)s

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
<b>Group:</b> <a href="../%(categoryidx)s">%(category)s</a><br />
<b>Maintainer:</b> <a href="/packager/persona/%(authority)s/">%(authority)s</a><br />
</small>

#(packagelist)s
<?_foot()?>
'''

def convgroup(str):
	return str.translate(string.maketrans('/ ','-.')).lower()

sys.stdout = os.fdopen(1, 'w', 0)

con = sqlite.connect(specdb)
cur = con.cursor()

cur.execute('select distinct category from spec order by category')

try: os.mkdir(htmldir)
except: pass

for cat in cur.fetchall():
	rec = { 'category': cat[0] }
	open(os.path.join(htmldir, convgroup(cat[0])) + '.php', 'w').write(category_template % rec)
	cur.execute('select distinct name, summary, description, authority, version, release, license, category, url from spec where category = "%s" order by name, version, release' % cat[0])
	for data in cur.fetchall():
		try: os.mkdir(os.path.join(htmldir, data[0]))
		except: pass

		rec = { 'categoryidx': convgroup(cat[0])}
		for h in headers: rec[h] = data[headers.index(h)]
		open(os.path.join(htmldir, data[0], 'index.php'), 'w').write(package_template % rec)
cur.close()
con.close()
