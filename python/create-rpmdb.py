#!/usr/bin/python

import glob, sqlite, sys, re, os, string, rpm

packagedir = '/dar/packages/'
rpmdb = '/dar/tmp/state/rpmdb.sqlite'

rpmhdr = {
	'filename':	100,
	'name':		40,
	'version':	15,
	'release':	15,
	'arch':		8,
	'repo':		5,
	'dist':		5,
#	'packager':	100,
#	'distribution':	100,
#	'vendor':	100,
#	'sourcerpm':	100,
}

infohdr = {
	'name':		40,
	'summary':	100,
	'description':	1024,
	'url':		100,
	'category':	40,
	'parent':	40,
}

userpm404 = 0

if sys.version[0] == "2" and not userpm404:
	ts = rpm.TransactionSet("", (rpm._RPMVSF_NOSIGNATURES or rpm.RPMVSF_NOHDRCHK or rpm._RPMVSF_NODIGESTS or rpm.RPMVSF_NEEDPAYLOAD))


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
	if sys.version[0] == "2" and not userpm404:
		h = ts.hdrFromFdno(fd)
		issrc = h[rpm.RPMTAG_SOURCEPACKAGE]
	else:
		(h, issrc) = rpm.headerFromPackage(fd)
	os.close(fd)
	return (h, issrc)

def readrpm(file):
	(header, issrc) = getHeader(file)
	rec = {
		'filename': os.path.basename(file),
		'parent': os.path.basename(os.path.dirname(file)),
		'name': header[rpm.RPMTAG_NAME],
		'arch': header[rpm.RPMTAG_ARCH],
		'version': header[rpm.RPMTAG_VERSION],
		'release': header[rpm.RPMTAG_RELEASE],
		'summary': header[rpm.RPMTAG_SUMMARY].replace('"', '\''),
		'description': header[rpm.RPMTAG_DESCRIPTION].replace('"', '\''),
		'buildtime': header[rpm.RPMTAG_BUILDTIME],
		'buildhost': header[rpm.RPMTAG_BUILDHOST],
		'category': header[rpm.RPMTAG_GROUP],
		'packager': header[rpm.RPMTAG_PACKAGER],
		'distribution': header[rpm.RPMTAG_DISTRIBUTION],
		'vendor': header[rpm.RPMTAG_VENDOR],
		'license': header[rpm.RPMTAG_LICENSE],
		'url': header[rpm.RPMTAG_URL],
		'sourcerpm': header[rpm.RPMTAG_SOURCERPM],
	}
#	rec.update(re.search('(?P<name>.+)-(?P<version>[\w\.]+)-(?P<release>[\w\.]+)\.(?P<arch>\w+).rpm$', rpm).groupdict())
	if issrc: rec['arch'] = 'src'
	rec['repo'] = repo(file)
	if rec['arch'] in ('src', 'nosrc'): 
		rec['dist'] = rec['arch']
	else:
		rec['dist'] = dist(file)
	return rec

sys.stdout = os.fdopen(1, 'w', 0)

droprpmsta = 'drop table rpm'
dropinfosta = 'drop table info'
createrpmsta = 'create table rpm ( '
for key in rpmhdr.keys(): createrpmsta += '%s varchar(%d), ' % (key, rpmhdr[key])
createrpmsta = createrpmsta.rstrip(', ') + ' )'

createinfosta = 'create table info ( '
for key in infohdr.keys(): createinfosta += '%s varchar(%d), ' % (key, infohdr[key])
createinfosta = createinfosta.rstrip(', ') + ' )'

insertrpmsta = 'insert into rpm ( '
for key in rpmhdr.keys(): insertrpmsta += '%s, ' % key
insertrpmsta = insertrpmsta.rstrip(', ') + ' ) values ( '
for key in rpmhdr.keys(): insertrpmsta += '"%%(%s)s", ' % key
insertrpmsta = insertrpmsta.rstrip(', ') + ' )'

insertinfosta = 'insert into info ( '
for key in infohdr.keys(): insertinfosta += '%s, ' % key
insertinfosta = insertinfosta.rstrip(', ') + ' ) values ( '
for key in infohdr.keys(): insertinfosta += '"%%(%s)s", ' % key
insertinfosta = insertinfosta.rstrip(', ') + ' )'

con = sqlite.connect(rpmdb)
cur = con.cursor()
try: cur.execute(droprpmsta)
except: pass
try: cur.execute(dropinfosta)
except: pass
cur.execute(createrpmsta)
cur.execute(createinfosta)

for file in glob.glob(os.path.join(packagedir, '*/*.rpm')):
	try:
		rec = readrpm(file)
	except:
		print file, 'FAILED'
		continue
	cur.execute(insertrpmsta % rec)
	cur.execute('select distinct name from info where name = %(name)s' % rec)
	list = cur.fetchall()
	if not list:
		cur.execute(insertinfosta % rec)

con.commit()
con.close()
