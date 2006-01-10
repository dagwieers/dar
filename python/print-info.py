#!/usr/bin/python

import glob, sqlite, sys, re, os, string
import darlib

sys.stdout = os.fdopen(1, 'w', 0)

con, cur = darlib.opendb()

print 'General info'
cur.execute('select distinct name from spec order by name')
tot = len(cur.fetchall())
print '  Number of SPEC files:', tot

cur.execute('select distinct category from spec order by name')
print '  Number of categories:', len(cur.fetchall())

cur.execute('select name from pkg')
tot2 = len(cur.fetchall())
print '  Number of packages:', tot2

cur.execute('select distinct name from pkg')
print '  Number of unique packages:', len(cur.fetchall())

cur.execute('select distinct name from pkg where arch = "src"')
print '  Number of unique source packages:', len(cur.fetchall())

print
print 'Arch stats:'
cur.execute('select distinct arch from pkg order by arch')
for arch, in cur.fetchall():
	cur.execute('select * from pkg where arch = "%s"' % arch)
	print '  %s has %d packages' % (arch, len(cur.fetchall()))

print
print 'Dist stats:'
cur.execute('select distinct dist from pkg order by dist')
for dist, in cur.fetchall():
	if dist in ('0', 'nosrc', 'src'): continue
	if dist in ('rh6', 'rh7', 'rh8', 'rh9', 'el2', 'el3', 'el4', 'fc1', 'fc2', 'fc3', 'fc4', 'fc5'):
		cur.execute('select distinct name from pkg where (dist = "%s" or dist = "0") and ( repo = "rf" or repo = "dag" or repo = "dries" ) and ( arch = "i386" or arch = "i586" or arch = "i686" or arch = "athlon" or arch = "noarch" or arch = "nosrc" )' % dist)
		print '  %s-i386 has %d packages' % (dist, len(cur.fetchall()))
	if dist in ('el3', 'el4', 'fc2', 'fc3', 'fc4', 'fc5'):
		cur.execute('select distinct name from pkg where (dist = "%s" or dist = "0") and ( repo = "rf" or repo = "dag" or repo = "dries" ) and ( arch = "x86_64" or arch = "noarch" or arch = "nosrc" )' % dist)
		print '  %s-x86_64 has %d packages' % (dist, len(cur.fetchall()))
	if dist in ('au1.91', 'au1.92'):
		cur.execute('select distinct name from pkg where (dist = "%s" or dist = "0") and ( repo = "rf" or repo = "dag" or repo = "dries" ) and ( arch = "sparc" or arch = "noarch" or arch = "nosrc" )' % dist)
		print '  %s-sparc has %d packages' % (dist, len(cur.fetchall()))

print
print 'Packager activity:'
cur.execute('select distinct authority from spec order by authority')
for authority, in cur.fetchall():
	if authority:
		cur.execute('select distinct parent from spec where authority = "%s"' % authority)
		nr = len(cur.fetchall())
		print '  %s maintains %d packages (%.1f%%)' % (authority, nr, nr * 100.0 / tot)

print
print 'Builder activity:'
cur.execute('select distinct builder from pkg order by builder')
for builder, in cur.fetchall():
	if builder:
		cur.execute('select * from pkg where builder = "%s"' % builder)
		nr = len(cur.fetchall())
		print '  %s builds %d packages (%.1f%%)' % (builder, nr, nr * 100.0 / tot2)

### Debug printing
#cur.execute('select distinct name, epoch, version, release, url from spec order by name')
#for all in cur.fetchall():
#	print all

#print
#print 'Print summaries:'
#cur.execute('select distinct name, summary from spec order by name')
#for pkg in cur.fetchall():
#	print '  %s: %s' % (pkg[0], pkg[1])
