#!/usr/bin/python

import glob, sqlite, sys, re, os, string, rpm

print 'This script is obsolete.'
sys.exit(1)

packagedir = '/dar/packages/'

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

ts = rpm.TransactionSet("", (rpm._RPMVSF_NOSIGNATURES or rpm.RPMVSF_NOHDRCHK or rpm._RPMVSF_NODIGESTS or rpm.RPMVSF_NEEDPAYLOAD))
infocon, infocur = darlib.opendb('info', create=True)

#createsta = 'create table info ( name varchar(10) unique primary key, '
#for key in infohdr[1:]: createsta += '%s varchar(10), ' % key
#createsta = createsta.rstrip(', ') + ' )'

for file in glob.glob(os.path.join(packagedir, '*/*.rpm')):
	inforec = readfile(file)
	infocur.execute('select distinct name from info where name = "%(name)s"' % inforec)
	if infocur.fetchall(): continue
	try:
		inforec = readrpm(file)
	except:
		print file, 'FAILED'
		continue
	darlib.insertdb(infocur, 'info', inforec)

infocon.commit()
