#!/usr/bin/python

import glob, sqlite, sys, re, os, string, rpm
import darlib

print 'This script is obsolete.'
sys.exit(1)

packagedir = '/dar/packages/'

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

distlist = ['0', 'rh6', 'rh7', 'rh8', 'rh9', 'el2', 'el3', 'el4', 'fc1', 'fc2', 'fc3', 'fc4', 'fc5', 'au1.91', 'au1.92']
distlistre = '|'.join(distlist + distmap.keys())

def repo(filename):
        try:
                return re.search('\.(dag|dries|rf|test)\.\w+\.rpm$', filename).groups()[0]
        except: 
                try:
                        return re.search('\.(dag|dries|rf|test)\.('+distlistre+')\.\w+\.rpm$', filename).groups()[0]
                except: 
                        return None

def dist(filename):
        try:
                dist = re.search('\.('+distlistre+')\.(dag|dries|rf|test)\.\w+\.rpm$', filename).groups()[0]
        except: 
                try:
                        dist = re.search('\.(dag|dries|rf|test)\.(\w+)\.\w+\.rpm$', filename).groups()[1]
                except: 
                        dist = None
        if dist in distlist: return dist
	elif dist in distmap.keys(): return distmap[dist]
        else:   
                print 'Unknown distribution tag %s in filename %s' % (dist, filename)
		raise

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

rpmcon, rpmcur = darlib.opendb('rpm', create=True)
ts = rpm.TransactionSet("", (rpm._RPMVSF_NOSIGNATURES or rpm.RPMVSF_NOHDRCHK or rpm._RPMVSF_NODIGESTS or rpm.RPMVSF_NEEDPAYLOAD))

for file in glob.glob(os.path.join(packagedir, '*/*.rpm')):
	try:
		rpmrec = readrpm(file)
	except:
		print file, 'FAILED'
		continue
	darlib.insertdb(rpmcur, 'rpm', rpmrec)

rpmcon.commit()
