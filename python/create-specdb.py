#!/usr/bin/python

import glob, sqlite, sys, re, os, string

specdir = '/dar/rpms/'
specdb = '/dar/tmp/state/specdb.sqlite'

spechdr = ('authority', 'summary', 'name', 'version', 'release', 'license', 'category', 'url', 'description')

specre = {
	'authority':	r'^# Authority: (\w+)$',
	'summary':	r'^Summary: (.+)$',
	'name':		r'^Name: ([\w\-\+_]+)$',
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
		for key in specre.keys:
			rec[key] = re.search(specre[key], data, re.M).group(1).replace('"', '\'')
	except:
		print 'Error with key %s' % key
		raise
	return rec

dropsta = 'drop table spec'

### Create statement
createsta = 'create table spec ( '
for key in spechdr: createsta += '%s varchar(10), ' % key
createsta = createsta.rstrip(', ') + ' )'

### Insert statement
insertsta = 'insert into spec ( '
for key in spechdr: insertsta += '%s, ' % key
insertsta = insertsta.rstrip(', ') + ' ) values ( '
for key in spechdr: insertsta += '"%%(%s)s", ' % key
insertsta = insertsta.rstrip(', ') + ' )'

speccon = sqlite.connect(specdb)
speccur = speccon.cursor()
try: speccur.execute(dropsta)
except: pass
speccur.execute(createsta)

for file in glob.glob(os.path.join(specdir, '*/*.spec')):
	data = open(file, 'r').read(50000)
	try:
		rec = readspec(data)
	except:
		print file, 'FAILED'
		continue
	speccur.execute(insertsta % rec)

speccon.commit()
speccur.close()
speccon.close()
