#!/usr/bin/python

import glob, sqlite, sys, re, os, string, rpm

def vercmp((e1, v1, r1), (e2, v2, r2)):
	rc = rpm.labelCompare((e1, v1, r1), (e2, v2, r2))
	return rc

sys.stdout = os.fdopen(1, 'w', 0)

con = sqlite.connect('/dar/pub/info/state/pkgdb.sqlite')
cur = con.cursor()

cur.execute('select distinct name from pkg order by name')
for name in cur.fetchall():
#	print 'Processing', name[0]
	cur.execute('select filename, arch, version, release, dist, repo from pkg where name = "%s" and arch != "src" order by dist, version, release, arch' % name[0])
	filename = 0
	arch = 1
	version = 2
	release = 3
	dist = 4
	repo = 5
	pkgs = cur.fetchall()
	for pkg1 in pkgs:
		if pkg1[arch] == 'nosrc': continue
		if pkg1[repo] == 'test': continue
		if pkg1[filename].find('kernel') == 0: continue
		for pkg2 in pkgs:
			if pkg2[arch] == 'nosrc': continue
			if pkg2[repo] == 'test': continue
			if pkg1[filename] == pkg2[filename]: continue
			if pkg1[dist] != pkg2[dist]: continue
			if pkg1[arch] != pkg2[arch]: continue
			if vercmp(('0', pkg1[version], pkg1[release]), ('0', pkg2[version], pkg2[release])) > 0:
				print '%s deprecated by %s' % (pkg2[filename], pkg1[filename])

cur.close()
con.close()
