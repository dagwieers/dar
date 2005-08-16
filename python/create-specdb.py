#!/usr/bin/python

import glob, sqlite, sys, re, os, string

sizes = {
	'authority':15,
	'summary':100,
	'name':40,
	'version':15,
	'release':15,
	'license':20,
	'category':30,
	'url':50,
#	'description':1024,
}

regs = {
	'authority': '^# Authority: (\w+)$',
	'summary': '^Summary: (.+)$',
	'name': '^Name: ([\w\-_]+)$',
	'version': '^Version: ([^\s]+)$',
	'release': '^Release: ([^\s]+)$',
	'license': '^License: (.+)$',
	'category': '^Group: (.+)$',
	'url': '^URL: ([^\s]+)$',
	'description': '^%description:\n([.\n]+)\n\n%',
}

def readspec(data):
	rec = {}
	try:
		for key in sizes.keys():
			rec[key] = re.search(regs[key], data, re.M).group(1).replace('"', '\'')
	except:
		print 'Error with key %s' % key
		raise
	return rec

dropsta = 'drop table spec'
createsta = 'create table spec ( '
for key in sizes.keys(): createsta += '%s varchar(%d), ' % (key, sizes[key])
createsta = createsta.rstrip(', ') + ' )'

insertsta = 'insert into spec ( '
for key in sizes.keys(): insertsta += '%s, ' % key
insertsta = insertsta.rstrip(', ') + ' ) values ( '
for key in sizes.keys(): insertsta += '"%%(%s)s", ' % key
insertsta = insertsta.rstrip(', ') + ' )'

con = sqlite.connect('/dar/pub/info/state/specdb.sqlite')
cur = con.cursor()
cur.execute(dropsta)
cur.execute(createsta)

for file in glob.glob('/dar/rpms/*/*.spec'):
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
