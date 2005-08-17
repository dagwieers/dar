#!/usr/bin/python

import glob, sqlite, sys, re, os, string, rpm

packagedir = '/dar/packages/'
rpmdb = '/dar/tmp/state/rpmdb.sqlite'

rpmhdr = ('name', 'version', 'release', 'arch', 'repo', 'dist', 'epoch')

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
                return None

def getHeader(filename):
	'''Read a rpm header.'''
	fd = os.open(filename, os.O_RDONLY)
	h = ts.hdrFromFdno(fd)
	os.close(fd)
	return h

def readrpm(file):
	header = getHeader(file)
	rec = {
#		'filename': os.path.basename(file),
#		'parent': os.path.basename(os.path.dirname(file)),
		'name': header[rpm.RPMTAG_NAME],
		'arch': header[rpm.RPMTAG_ARCH],
		'version': header[rpm.RPMTAG_VERSION],
		'release': header[rpm.RPMTAG_RELEASE],
#		'summary': header[rpm.RPMTAG_SUMMARY].replace('"', '\''),
#		'description': header[rpm.RPMTAG_DESCRIPTION].replace('"', '\''),
#		'buildtime': header[rpm.RPMTAG_BUILDTIME],
#		'buildhost': header[rpm.RPMTAG_BUILDHOST],
#		'category': header[rpm.RPMTAG_GROUP],
#		'packager': header[rpm.RPMTAG_PACKAGER],
#		'distribution': header[rpm.RPMTAG_DISTRIBUTION],
#		'vendor': header[rpm.RPMTAG_VENDOR],
#		'license': header[rpm.RPMTAG_LICENSE],
#		'url': header[rpm.RPMTAG_URL],
#		'sourcerpm': header[rpm.RPMTAG_SOURCERPM],
		'epoch': header[rpm.RPMTAG_EPOCH],
	}
#	rec.update(re.search('(?P<name>.+)-(?P<version>[\w\.]+)-(?P<release>[\w\.]+)\.(?P<arch>\w+).rpm$', rpm).groupdict())
	if header[rpm.RPMTAG_SOURCEPACKAGE]: rec['arch'] = 'src'
	rec['repo'] = repo(file)
	if rec['arch'] in ('src', 'nosrc'): 
		rec['dist'] = rec['arch']
	else:
		rec['dist'] = dist(file)
	return rec


sys.stdout = os.fdopen(1, 'w', 0)

ts = rpm.TransactionSet("", (rpm._RPMVSF_NOSIGNATURES or rpm.RPMVSF_NOHDRCHK or rpm._RPMVSF_NODIGESTS or rpm.RPMVSF_NEEDPAYLOAD))

dropsta = 'drop table rpm'
createsta = 'create table rpm ( '
for key in rpmhdr: createsta += '%s varchar(10), ' % key
createsta = createsta.rstrip(', ') + ' )'

insertsta = 'insert into rpm ( '
for key in rpmhdr: insertsta += '%s, ' % key
insertsta = insertsta.rstrip(', ') + ' ) values ( '
for key in rpmhdr: insertsta += '"%%(%s)s", ' % key
insertsta = insertsta.rstrip(', ') + ' )'

rpmcon = sqlite.connect(rpmdb)
rpmcur = rpmcon.cursor()
try: rpmcur.execute(dropsta)
except: pass
rpmcur.execute(createsta)

for file in glob.glob(os.path.join(packagedir, '*/*.rpm')):
	try:
		rec = readrpm(file)
	except:
		print file, 'FAILED'
		continue
	rpmcur.execute(insertsta % rec)

rpmcon.commit()
rpmcur.close()
rpmcon.close()
