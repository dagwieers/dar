#!/usr/bin/python

import glob, sqlite, sys, re, os, string

def convgroup(str):
	return str.translate(string.maketrans('/ ','-.'))

sys.stdout = os.fdopen(1, 'w', 0)

htmldir = '/dar/tmp/html'

con = sqlite.connect('/dar/pub/info/state/specdb.sqlite')
cur = con.cursor()

cur.execute('select distinct category from spec order by category')
cats = cur.fetchall()

try: os.mkdir(htmldir)
except: pass

for cat in cats:
	open(os.path.join(htmldir, convgroup(cat[0])) + '.php', 'w').write(cat[0])
	cur.execute('select distinct name from spec where category = "%s" order by name, version, release' % cat[0])
	names = cur.fetchall()
	for name in names:
		try: os.mkdir(os.path.join(htmldir, name[0]))
		except: pass
		open(os.path.join(htmldir, name[0], 'index.php'), 'w').write(cat[0]+'/'+name[0])
cur.close()
con.close()
