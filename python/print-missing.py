#!/usr/bin/python

import glob, sqlite, sys, re, os, string, rpm
import darlib

packagedir = '/dar/packages'

try: builder1 = sys.argv[1]
except: builder1 = 'dag'

try: builder2 = sys.argv[2]
except: builder2 = 'dries'

distmap = {
        'rhfc1': 'fc1',
        'rhel3': 'el3',
        'rhel2.1': 'el2',
        'rhas21': 'el2',
        'rh90': 'rh9',
        'rh80': 'rh8',
        'rh73': 'rh7',
        'rh62': 'rh6',
}

archmap = {
	'noarch': 'i',
	'i386': 'i',
	'i486': 'i',
	'i586': 'i',
	'i686': 'i',
	'i386': 'i',
	'x86_64': 'a',
	'sparc': 's',
	'ppc': 'p',
}

disttaglist = distmap.keys() + [ '0.el2', '0.rh6', '0.rh7', '0.rh8', '0.rh9',
				'1.el3', '1.fc1', '1.fc2', '1.fc3',
				'2.el4', '2.fc4', '2.fc5', '2.fc6',
				'3.el5', '3.fc7', '3.fc8', '3.fc9' ]

def vercmp((e1, v1, r1), (e2, v2, r2)):
#	print '%s, %s, %s vs %s, %s, %s' % (e1, v1, r1, e2, v2, r2)
	return rpm.labelCompare((e1, v1, r1), (e2, v2, r2))

def filename(rec):
	return '%(parent)s/%(name)s-%(version)s-%(release)s.%(arch)s.rpm' % rec

sys.stdout = os.fdopen(1, 'w', 0)

con = sqlite.connect(darlib.dbase)
pkgcur = darlib.opentb(con, 'pkg')

missinglist = []
oldname = ''
oldarch = ''
oldparent = ''

pkgcur.execute('select distinct dist, arch from pkg where builder = "%s" order by dist, arch' % builder1)
builder1dists = []
for set in pkgcur.fetchall(): builder1dists.append(set)

pkgcur.execute('select distinct dist, arch from pkg where builder = "%s" order by dist, arch' % builder2)
builder2dists = []
for set in pkgcur.fetchall(): builder2dists.append(set)

builderdists = []
for set in builder1dists:
	if set in builder2dists:
		builderdists.append(set)

builderdists.remove(('src','src'))

#print 'Comparing dists:',
#for dist, arch in builderdists:
#	print dist+archmap[arch],
#print

pkgcur.execute('select parent, name, dist, arch from pkg where builder = "%s" order by parent, name, dist' % builder2)
for parent, name, dist, arch in pkgcur.fetchall():
#	if parent.find('gno') != 0: continue
	if parent.find('kernel') == 0: continue
	if name.rfind('debuginfo') >= 0: continue

	if (dist, arch) not in builderdists: continue

	if missinglist and oldname != name:
		print oldname, 
#		for entry in missinglist: print entry,
		print ','.join(missinglist)
		missinglist = []

	### Don't handle subpackages
	if oldparent == parent and oldname != name: continue

	A = {}
	B = { 'version': '0', 'release': '0' }
	C = {}
	D = { 'version': '0', 'release': '0' }

	pkgcur.execute('select version, release, repo from pkg where name = "%s" and arch = "%s" and dist = "%s" and builder = "%s" order by version, release' % (name, arch, dist, builder2))
	for A['version'], A['release'], A['repo'] in pkgcur.fetchall():
	        ### Clean up release tag :(
		for disttag in disttaglist:
			A['release'] = A['release'].replace('.'+disttag+'.'+A['repo'], '')
			A['release'] = A['release'].replace('.'+A['repo']+'.'+disttag, '')
		if vercmp(('0', A['version'], A['release']), ('0', B['version'], B['release'])) > 0:
			B = A.copy()

	pkgcur.execute('select version, release, repo from pkg where name = "%s" and arch = "%s" and dist = "%s" and builder = "%s" order by version, release' % (name, arch, dist, builder1))
	for C['version'], C['release'], C['repo'] in pkgcur.fetchall():
	        ### Clean up release tag :(
		for disttag in disttaglist:
			C['release'] = C['release'].replace('.'+disttag+'.'+C['repo'], '')
			C['release'] = C['release'].replace('.'+C['repo']+'.'+disttag, '')
		if vercmp(('0', C['version'], C['release']), ('0', D['version'], D['release'])) > 0:
			D = C.copy()

#	print name, '\t', dist, '  dr:', B, '\tda:', D
	if vercmp(('0', B['version'], B['release']), ('0', D['version'], D['release'])) > 0:
		missinglist.append(dist+archmap[arch])

	oldname = name
	oldparent = parent

#	break
