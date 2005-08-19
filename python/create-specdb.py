#!/usr/bin/python

import glob, sqlite, sys, re, os, string, shutil

#specdir = '/dar/packages/'
specdir = '/dar/rpms/'
specdb = '/dar/tmp/state/specdb.sqlite'

spechdr = ('name', 'authority', 'summary', 'version', 'release', 'license', 'category', 'url', 'description', 'upstream', 'parent')

specre = {
	'authority':	'^# Authority: (\w+)$',
	'upstream':	'^# Upstream: (.+?)$',
	'summary':	'^Summary: (.+?)$',
	'name':		'^Name: ([\w\-\+_]+)$',
	'parent':	'^Name: ([\w\-\+_]+)$',
	'version':	'^Version: ([^\s]+)$',
	'release':	'^Release: ([^\s]+)$',
	'license':	'^License: (.+?)$',
	'category':	'^Group: (.+?)$',
	'url':		'^URL: ([^\s]+)$',
	'description':	'^%description\n(.+?)\n\n%',
}

def readspec(file):
	data = open(file, 'r').read(50000)
	rec = {}
	try:
		for key in specre.keys():
			rec[key] = ''
		for key in specre.keys():
			rec[key] += re.search(specre[key], data, re.M | re.DOTALL).group(1).replace('"', '\'')
	except:
		if key in ('upstream', ):
			pass
		elif key in ('url', ):
			print 'Error with key "%s" in "%s"' % (key, file)
		else:
			print 'Error with key "%s" in "%s"' % (key, file)
			raise
	if not rec['upstream']: rec['upstream'] = 'packagers@list.rpmforge.net'
	return rec

sys.stdout = os.fdopen(1, 'w', 0)

createsta = 'create table info ( name varchar(10) unique primary key, '
for key in spechdr[1:]: createsta += '%s varchar(10), ' % key
createsta = createsta.rstrip(', ') + ' )'

insertsta = 'insert into info ( '
for key in spechdr: insertsta += '%s, ' % key
insertsta = insertsta.rstrip(', ') + ' ) values ( '
for key in spechdr: insertsta += '"%%(%s)s", ' % key
insertsta = insertsta.rstrip(', ') + ' )'

speccon = sqlite.connect(specdb + '.tmp')
speccur = speccon.cursor()
speccur.execute(createsta)

for file in glob.glob(os.path.join(specdir, '*/*.spec')):
	try:
		rec = readspec(file)
	except:
		print file, 'FAILED'
		continue
	try: speccur.execute(insertsta % rec)
	except: pass
		
speccon.commit()
os.rename(specdb + '.tmp', specdb)
