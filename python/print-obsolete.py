#!/usr/bin/python

import glob, sqlite, sys, re, os, string, rpm
import darlib

packagedir = '/dar/packages'

try: builder = sys.argv[1]
except: builder = 'dag'

def vercmp((e1, v1, r1), (e2, v2, r2)):
	return rpm.labelCompare((e1, v1, r1), (e2, v2, r2))

def filename(rec):
	return '%(parent)s/%(name)s-%(version)s-%(release)s.%(arch)s.rpm' % rec

sys.stdout = os.fdopen(1, 'w', 0)

con = sqlite.connect(darlib.dbase)
pkgcur = darlib.opentb(con, 'pkg')

pkgcur.execute('select distinct name, parent, builder from pkg order by parent, name')
for name, parent, builder in pkgcur.fetchall():
	if parent.find('kernel') == 0: continue
	pkgcur.execute('select name, arch, version, release, dist, repo, parent from pkg where name = "%s" and builder = "%s" and arch != "src" order by dist, version, release, arch' % (name, builder))
	pkgs = pkgcur.fetchall()
	A = {}
	obsoletelist = []
	for A['name'], A['arch'], A['version'], A['release'], A['dist'], A['repo'], A['parent'] in pkgs:
		if A['arch'] == 'nosrc': continue
		if A['repo'] == 'test': continue
		B = {}
		for B['name'], B['arch'], B['version'], B['release'], B['dist'], B['repo'], B['parent'] in pkgs:
			if B['arch'] == 'nosrc': continue
			if B['repo'] == 'test': continue
			if A == B: continue
			if A['dist'] != B['dist']: continue
			if A['arch'] != B['arch']: continue
			if vercmp(('0', A['version'], A['release']), ('0', B['version'], B['release'])) >= 0:
				if filename(B) not in obsoletelist:
					obsoletelist.append(filename(B))
	if obsoletelist:
		obsoletelist.sort()
		for file in obsoletelist:
			print os.path.join(packagedir, file)
