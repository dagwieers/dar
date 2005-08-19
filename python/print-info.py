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
speccur.execute('select distinct name from info order by name')
tot = len(speccur.fetchall())
print '  Number of SPEC files:', tot

speccur.execute('select distinct category from info order by name')
print '  Number of categories:', len(speccur.fetchall())

pkgcur.execute('select name from rpm')
print '  Number of packages:', len(pkgcur.fetchall())

pkgcur.execute('select distinct name from rpm')
print '  Number of unique packages:', len(pkgcur.fetchall())

pkgcur.execute('select distinct name from rpm where arch = "src"')
print '  Number of unique source packages:', len(pkgcur.fetchall())

print
print 'Arch stats:'
pkgcur.execute('select distinct arch from rpm order by arch')
for arch, in pkgcur.fetchall():
	pkgcur.execute('select * from rpm where arch = "%s"' % arch)
	print '  %s has %d packages' % (arch, len(pkgcur.fetchall()))

print
print 'Dist stats:'
pkgcur.execute('select distinct dist from rpm order by dist')
for dist, in pkgcur.fetchall():
	if dist in ('0', 'nosrc', 'src', 'fc4'): continue
	pkgcur.execute('select distinct name from rpm where (dist = "%s" or dist = "0") and ( repo = "rf" or repo = "dag" ) and ( arch = "i386" or arch = "i586" or arch = "i686" or arch = "athlon" or arch = "noarch" or arch = "nosrc" )' % dist)
	print '  %s-i386 has %d packages' % (dist, len(pkgcur.fetchall()))
	if dist in ('rh6', 'rh8', 'rh7', 'rh9', 'el2', 'fc1', 'fc4'): continue
	pkgcur.execute('select distinct name from rpm where (dist = "%s" or dist = "0") and ( repo = "rf" or repo = "dag" ) and ( arch = "x86_64" or arch = "noarch" or arch = "nosrc" )' % dist)
	print '  %s-x86_64 has %d packages' % (dist, len(pkgcur.fetchall()))

print
print 'Packager activity:'
speccur.execute('select distinct authority from info order by authority')
for authority, in speccur.fetchall():
	if authority:
		speccur.execute('select distinct parent from info where authority = "%s"' % authority)
		nr = len(speccur.fetchall())
		print '  %s maintains %d packages (%.1f%%)' % (authority, nr, nr * 100.0 / tot)

#print
#print 'Print summaries:'
#speccur.execute('select distinct name, summary from spec order by name')
#for pkg in speccur.fetchall():
#	print '  %s: %s' % (pkg[0], pkg[1])
