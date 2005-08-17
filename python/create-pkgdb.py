#!/usr/bin/python

import glob, sqlite, sys, re, os, string

packagedir = '/dar/packages/'
pkgdb = '/dar/tmp/state/pkgdb.sqlite'

pkghdr = ('filename', 'name', 'version', 'release', 'arch', 'repo', 'dist')

#pkghdr = {
##	'filename':100,
#	'name':40,
#	'version':15,
#	'release':15,
#	'arch':8,
#	'repo':5,
#	'dist':5,
#}

def repo(filename):
        try:
                return re.search('.(dag|rf|test).\w+.rpm$', filename).groups()[0]
        except: 
                try:
                        return re.search('.(dag|rf|test).(\w+|rhel2\.1).\w+.rpm$', filename).groups()[0]
                except: 
                        return None

def dist(filename):
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
        try:
                dist = re.search('.(\w+|rhel2\.1).(dag|rf|test).\w+.rpm$', filename).groups()[0]
        except: 
                try:
                        dist = re.search('.(dag|rf|test).(\w+).\w+.rpm$', filename).groups()[1]
                except: 
                        dist = None
        if dist in ('0', 'rh6', 'rh7', 'rh8', 'rh9', 'el2', 'el3', 'el4', 'fc1', 'fc2', 'fc3', 'fc4'): return dist
	elif dist in distmap.keys(): return distmap[dist]
        else:   
                print 'Unknown distribution tag %s in filename %s' % (dist, filename)
		raise

def readfile(file):
	rec = {
		'filename': os.path.basename(file),
		'parent': os.path.basename(os.path.dirname(file)),
	}
	rec.update(re.search('(?P<name>[^/]+)-(?P<version>[\w\.]+)-(?P<release>[\w\.]+)\.(?P<arch>\w+).rpm$', file).groupdict())
	rec['repo'] = repo(file)
	if rec['arch'] in ('src', 'nosrc'): 
		rec['dist'] = rec['arch']
	else:
		rec['dist'] = dist(file)
	return rec

sys.stdout = os.fdopen(1, 'w', 0)

dropsta = 'drop table pkg'
createsta = 'create table pkg ( '
for key in pkghdr: createsta += '%s varchar(10), ' % key
createsta = createsta.rstrip(', ') + ' )'

insertsta = 'insert into pkg ( '
for key in pkghdr: insertsta += '%s, ' % key
insertsta = insertsta.rstrip(', ') + ' ) values ( '
for key in pkghdr: insertsta += '"%%(%s)s", ' % key
insertsta = insertsta.rstrip(', ') + ' )'

pkgcon = sqlite.connect(pkgdb)
pkgcur = pkgcon.cursor()
try: pkgcur.execute(dropsta)
except: pass
pkgcur.execute(createsta)

for file in glob.glob(os.path.join(packagedir, '*/*.rpm')):
	try:
		rec = readfile(file)
	except:
		print file, 'FAILED'
		continue
	pkgcur.execute(insertsta % rec)

pkgcon.commit()
pkgcur.close()
pkgcon.close()
