#!/usr/bin/python

import glob, sqlite, sys, re, os, string, rpm

packagedir = '/dar/packages/'
infodb = '/dar/tmp/state/infodb.sqlite'

infohdr = ('name', 'summary', 'description', 'url', 'license', 'category', 'parent')

ts = rpm.TransactionSet("", (rpm._RPMVSF_NOSIGNATURES or rpm.RPMVSF_NOHDRCHK or rpm._RPMVSF_NODIGESTS or rpm.RPMVSF_NEEDPAYLOAD))

def readfile(file):
	return re.search('(?P<name>[^/]+)-(?P<version>[\w\.]+)-(?P<release>[\w\.]+)\.(?P<arch>\w+).rpm$', file).groupdict()

def getHeader(filename):
	'''Read a rpm header.'''
	fd = os.open(filename, os.O_RDONLY)
	h = ts.hdrFromFdno(fd)
	os.close(fd)
	return h

def readrpm(file):
	header = getHeader(file)
	rec = {
		'parent': os.path.basename(os.path.dirname(file)),
		'name': header[rpm.RPMTAG_NAME],
		'summary': header[rpm.RPMTAG_SUMMARY].replace('"', '\''),
		'description': header[rpm.RPMTAG_DESCRIPTION].replace('"', '\''),
		'category': header[rpm.RPMTAG_GROUP],
		'license': header[rpm.RPMTAG_LICENSE],
		'url': header[rpm.RPMTAG_URL],
	}
	return rec

sys.stdout = os.fdopen(1, 'w', 0)

dropsta = 'drop table info'

createsta = 'create table info ( '
for key in infohdr: createsta += '%s varchar(10), ' % key
createsta = createsta.rstrip(', ') + ' )'

insertsta = 'insert into info ( '
for key in infohdr: insertsta += '%s, ' % key
insertsta = insertsta.rstrip(', ') + ' ) values ( '
for key in infohdr: insertsta += '"%%(%s)s", ' % key
insertsta = insertsta.rstrip(', ') + ' )'

infocon = sqlite.connect(infodb)
infocur = infocon.cursor()
try: infocur.execute(dropsta)
except: pass
infocur.execute(createsta)

for file in glob.glob(os.path.join(packagedir, '*/*.rpm')):
	rec = readfile(file)
	infocur.execute('select distinct name from info where name = "%(name)s"' % rec)
	if infocur.fetchall(): continue
	try:
		rec = readrpm(file)
	except:
		print file, 'FAILED'
		continue
	infocur.execute(insertsta % rec)

infocon.commit()
infocur.close()
infocon.close()
