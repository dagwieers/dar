#!/usr/bin/python

import glob, sqlite, sys, re, os, string, shutil
import darlib

#specdir = '/dar/packages/'
specdir = '/dar/rpms/'

specre = {
	'authority':	'^# Authority: (\w+)$',
	'upstream':	'^# Upstream: (.+?)$',
	'epoch':	'^Epoch: (\d+)$',
	'version':	'^Version: ([\w\.]+)$',
	'release':	'^Release: ([\w\.]+)$',
	'summary':	'^Summary: (.+?)$',
	'name':		'^Name: ([\w\-\+_]+)$',
	'parent':	'^Name: ([\w\-\+_]+)$',
	'license':	'^License: (.+?)$',
	'category':	'^Group: (.+?)$',
	'url':		'^URL: ([^\s]+)$',
	'description':	'^%description\n(.+?)\n\n%',
}

def readspec(file):
	data = open(file, 'r').read(50000)
	rec = {}
	for key in specre.keys():
		if not rec.has_key(key):
			rec[key] = ''
		try:
			rec[key] += re.search(specre[key], data, re.M | re.DOTALL).group(1).replace('"', '\'')
		except:
			if key in ('epoch', 'upstream'):
				pass
			elif key in ('url', ):
				print 'Error with key "%s" in "%s"' % (key, file)
			else:
				print 'Error with key "%s" in "%s" (FAILED)' % (key, file)
				raise
	if not rec['upstream']: rec['upstream'] = 'packagers@list.rpmforge.net'
	return rec

sys.stdout = os.fdopen(1, 'w', 0)

con = sqlite.connect(darlib.dbase)
speccur = darlib.opentb(con, 'spec', create=True)

#createsta = 'create table info ( name varchar(10) unique primary key, '
#for key in spechdr[1:]: createsta += '%s varchar(10), ' % key
#createsta = createsta.rstrip(', ') + ' )'

for file in glob.glob(os.path.join(specdir, '*/*.spec')):
	try:
		specrec = readspec(file)
	except:
#		print file, 'FAILED'
		continue
	try: 
		darlib.inserttb(speccur, 'spec', specrec)
	except: pass
		
con.commit()
