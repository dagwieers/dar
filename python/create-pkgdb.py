#!/usr/bin/python

import glob, sqlite, sys, re, os, string

sizes = {
	'filename':100,
	'name':40,
	'version':15,
	'release':15,
	'arch':8,
	'repo':5,
	'dist':5,
}

def repo(filename):
        try:
                return re.search('.(dag|rf|test).\w+.rpm$', filename).groups()[0]
        except: 
                try:
                        return re.search('.(dag|rf|test).(\w+|rhel2\.1).\w+.rpm$', filename).groups()[0]
                except: 
                        return None

def dist(filename):
        try:
                dist = re.search('.(\w+|rhel2\.1).(dag|rf|test).\w+.rpm$', filename).groups()[0]
        except: 
                try:
                        dist = re.search('.(dag|rf|test).(\w+).\w+.rpm$', filename).groups()[1]
                except: 
                        dist = None
        if dist in ('0', 'rh6', 'rh7', 'rh8', 'rh9', 'el2', 'el3', 'el4', 'fc1', 'fc2', 'fc3', 'fc4'): return dist
        elif dist == 'rhfc1': return 'fc1'
        elif dist == 'rhel3': return 'el3'
        elif dist == 'rhel2.1': return 'el2'
        elif dist == 'rhas21': return 'el2'
        elif dist == 'rh90': return 'rh9'
        elif dist == 'rh80': return 'rh8'
        elif dist == 'rh73': return 'rh7'
        elif dist == 'rh62': return 'rh6'
        else:   
                print 'Unknown distribution tag %s in filename %s' % (dist, filename)
                return None

def readfile(str):
	str = os.path.basename(str)
	rec = { 'filename': str }
	rec.update(re.search('(?P<name>.+)-(?P<version>[\w\.]+)-(?P<release>[\w\.]+)\.(?P<arch>\w+).rpm', str).groupdict())
	rec['repo'] = repo(str)
	if rec['arch'] in ('src', 'nosrc'): 
		rec['dist'] = rec['arch']
	else:
		rec['dist'] = dist(str)
	return rec

sys.stdout = os.fdopen(1, 'w', 0)

dropsta = 'drop table pkg'
createsta = 'create table pkg ( '
for key in sizes.keys(): createsta += '%s varchar(%d), ' % (key, sizes[key])
createsta = createsta.rstrip(', ') + ' )'

insertsta = 'insert into pkg ( '
for key in sizes.keys(): insertsta += '%s, ' % key
insertsta = insertsta.rstrip(', ') + ' ) values ( '
for key in sizes.keys(): insertsta += '"%%(%s)s", ' % key
insertsta = insertsta.rstrip(', ') + ' )'

con = sqlite.connect('/dar/pub/info/state/pkgdb.sqlite')
cur = con.cursor()
cur.execute(dropsta)
cur.execute(createsta)

for file in glob.glob('/dar/packages/*/*.rpm'):
	rec = readfile(file)
	if not rec:
		print file, 'FAILED'
		continue
	cur.execute(insertsta % rec)

con.commit()
con.close()
