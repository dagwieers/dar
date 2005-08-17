#!/usr/bin/python

import glob, sqlite, sys, re, os, string, rpm

pkgdb = '/dar/tmp/state/pkgdb.sqlite'

def vercmp((e1, v1, r1), (e2, v2, r2)):
	rc = rpm.labelCompare((e1, v1, r1), (e2, v2, r2))
	return rc

sys.stdout = os.fdopen(1, 'w', 0)

pkgcon = sqlite.connect(pkgdb)
pkgcur = pkgcon.cursor()

pkgcur.execute('select distinct name from pkg order by name')
for name, in pkgcur.fetchall():
#	print 'Processing', name
	pkgcur.execute('select filename, arch, version, release, dist, repo from pkg where name = "%s" and arch != "src" order by dist, version, release, arch' % name)
	pkgs = pkgcur.fetchall()
	A = {}
	obsoletelist = []
	for A['filename'], A['arch'], A['version'], A['release'], A['dist'], A['repo'] in pkgs:
		if A['arch'] == 'nosrc': continue
		if A['repo'] == 'test': continue
		if A['filename'].find('kernel') == 0: continue
		B = {}
		for B['filename'], B['arch'], B['version'], B['release'], B['dist'], B['repo'] in pkgs:
			if B['arch'] == 'nosrc': continue
			if B['repo'] == 'test': continue
			if A['filename'] == B['filename']: continue
			if A['dist'] != B['dist']: continue
			if A['arch'] != B['arch']: continue
			if vercmp(('0', A['version'], A['release']), ('0', B['version'], B['release'])) > 0:
				if B['filename'] not in obsoletelist:
					obsoletelist.append(B['filename'])
#				print '%s deprecated by %s' % (B['filename'], A['filename'])
	if obsoletelist:
#		print '%d %s' % (len(obsoletelist), name)
		obsoletelist.sort()
		for file in obsoletelist: print file

pkgcur.close()
pkgcon.close()
