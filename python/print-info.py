#!/usr/bin/python

import glob, sqlite, sys, re, os, string

specdb = '/dar/tmp/state/specdb.sqlite'
pkgdb = '/dar/tmp/state/pkgdb.sqlite'

sys.stdout = os.fdopen(1, 'w', 0)

speccon = sqlite.connect(specdb)
speccur = speccon.cursor()
pkgcon = sqlite.connect(pkgdb)
pkgcur = pkgcon.cursor()

print 'General info'
speccur.execute('select * from spec order by name')
print '  Number of SPEC files:', len(speccur.fetchall())

speccur.execute('select distinct category from spec order by name')
print '  Number of categories:', len(speccur.fetchall())

pkgcur.execute('select filename from pkg')
print '  Number of packages:', len(pkgcur.fetchall())

pkgcur.execute('select distinct name from pkg')
print '  Number of unique packages:', len(pkgcur.fetchall())

pkgcur.execute('select distinct name from pkg where arch = "src"')
print '  Number of unique source packages:', len(pkgcur.fetchall())

print
print 'Arch stats:'
pkgcur.execute('select distinct arch from pkg order by arch')
for arch in pkgcur.fetchall():
	pkgcur.execute('select * from pkg where arch = "%s"' % arch[0])
	print '  %s has %d packages' % (arch[0], len(pkgcur.fetchall()))

print
print 'Dist stats:'
pkgcur.execute('select distinct dist from pkg order by dist')
for dist in pkgcur.fetchall():
	if dist[0] in ('0', 'nosrc', 'src', 'fc4'): continue
	pkgcur.execute('select distinct name from pkg where (dist = "%s" or dist = "0") and ( repo = "rf" or repo = "dag" ) and ( arch = "i386" or arch = "i586" or arch = "i686" or arch = "athlon" or arch = "noarch" or arch = "nosrc" )' % dist[0])
	print '  %s-i386 has %d packages' % (dist[0], len(pkgcur.fetchall()))
	if dist[0] in ('rh6', 'rh8', 'rh7', 'rh9', 'el2', 'fc1', 'fc4'): continue
	pkgcur.execute('select distinct name from pkg where (dist = "%s" or dist = "0") and ( repo = "rf" or repo = "dag" ) and ( arch = "x86_64" or arch = "noarch" or arch = "nosrc" )' % dist[0])
	print '  %s-x86_64 has %d packages' % (dist[0], len(pkgcur.fetchall()))

print
print 'Packager activity:'
speccur.execute('select distinct authority from spec order by authority')
for name in speccur.fetchall():
	speccur.execute('select * from spec where authority = "%s"' % name[0])
	print '  %s maintains %d packages' % (name[0], len(speccur.fetchall()))

#print
#print 'Print summaries:'
#speccur.execute('select distinct name, summary from spec order by name')
#for pkg in speccur.fetchall():
#	print '  %s: %s' % (pkg[0], pkg[1])

speccur.close()
speccon.close()
pkgcur.close()
pkgcon.close()
