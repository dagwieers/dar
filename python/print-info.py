#!/usr/bin/python

import glob, sqlite, sys, re, os, string

sys.stdout = os.fdopen(1, 'w', 0)

con = sqlite.connect('/dar/pub/info/state/specdb.sqlite')
cur = con.cursor()
con2 = sqlite.connect('/dar/pub/info/state/pkgdb.sqlite')
cur2 = con2.cursor()

print 'General info'
cur.execute('select * from spec order by name')
print '  Number of SPEC files:', len(cur.fetchall())

cur.execute('select distinct category from spec order by name')
print '  Number of categories:', len(cur.fetchall())

cur2.execute('select filename from pkg')
print '  Number of packages:', len(cur2.fetchall())

cur2.execute('select distinct name from pkg')
print '  Number of unique packages:', len(cur2.fetchall())

cur2.execute('select distinct name from pkg where arch = "src"')
print '  Number of unique source packages:', len(cur2.fetchall())

print
print 'Arch stats:'
cur2.execute('select distinct arch from pkg order by arch')
for arch in cur2.fetchall():
	cur2.execute('select * from pkg where arch = "%s"' % arch[0])
	print '  %s has %d packages' % (arch[0], len(cur2.fetchall()))

print
print 'Dist stats:'
cur2.execute('select distinct dist from pkg order by dist')
for dist in cur2.fetchall():
	if dist[0] in ('0', 'nosrc', 'src', 'fc4'): continue
	cur2.execute('select distinct name from pkg where (dist = "%s" or dist = "0") and ( repo = "rf" or repo = "dag" ) and ( arch = "i386" or arch = "i586" or arch = "i686" or arch = "athlon" or arch = "noarch" or arch = "nosrc" )' % dist[0])
	print '  %s-i386 has %d packages' % (dist[0], len(cur2.fetchall()))
	if dist[0] in ('rh6', 'rh8', 'rh7', 'rh9', 'el2', 'fc1', 'fc4'): continue
	cur2.execute('select distinct name from pkg where (dist = "%s" or dist = "0") and ( repo = "rf" or repo = "dag" ) and ( arch = "x86_64" or arch = "noarch" or arch = "nosrc" )' % dist[0])
	print '  %s-x86_64 has %d packages' % (dist[0], len(cur2.fetchall()))

print
print 'Packager activity:'
cur.execute('select distinct authority from spec order by authority')
for name in cur.fetchall():
	cur.execute('select * from spec where authority = "%s"' % name[0])
	print '  %s packaged %d packages' % (name[0], len(cur.fetchall()))

#print
#print 'Print summaries:'
#cur.execute('select distinct name, summary from spec order by name')
#for pkg in cur.fetchall():
#	print '  %s: %s' % (pkg[0], pkg[1])

cur.close()
con.close()
