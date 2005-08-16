#!/usr/bin/python

import glob, sqlite, sys, re, os, string

specdir = '/dar/rpms/'
specdb = '/dar/tmp/state/specdb.sqlite'

spechdr = {
	'authority':	15,
	'summary':	100,
	'name':		40,
	'version':	15,
	'release':	15,
	'license':	20,
	'category':	30,
	'url':		50,
	'description':	1024,
}

regs = {
	'authority':	r'^# Authority: (\w+)$',
	'summary':	r'^Summary: (.+)$',
	'name':		r'^Name: ([\w\-_]+)$',
	'version':	r'^Version: ([^\s]+)$',
	'release':	r'^Release: ([^\s]+)$',
	'license':	r'^License: (.+)$',
	'category':	r'^Group: (.+)$',
	'url':		r'^URL: ([^\s]+)$',
	'description':	r'^%description\n(.+)',
}

def readspec(data):
	rec = {}
	try:
		for key in spechdr.keys():
			rec[key] = re.search(regs[key], data, re.M).group(1).replace('"', '\'')
	except:
		print 'Error with key %s' % key
		raise
	return rec

dropsta = 'drop table spec'

### Create statement
createsta = 'create table spec ( '
for key in spechdr.keys(): createsta += '%s varchar(%d), ' % (key, spechdr[key])
createsta = createsta.rstrip(', ') + ' )'

### Insert statement
insertsta = 'insert into spec ( '
for key in spechdr.keys(): insertsta += '%s, ' % key
insertsta = insertsta.rstrip(', ') + ' ) values ( '
for key in spechdr.keys(): insertsta += '"%%(%s)s", ' % key
insertsta = insertsta.rstrip(', ') + ' )'

con = sqlite.connect(specdb)
cur = con.cursor()
try: cur.execute(dropsta)
except: pass
cur.execute(createsta)

for file in glob.glob(os.path.join(specdir, '*/*.spec')):
	data = open(file, 'r').read(50000)
	try:
		rec = readspec(data)
	except:
		print file, 'FAILED'
		continue
	cur.execute(insertsta % rec)

con.commit()
cur.close()
con.close()
