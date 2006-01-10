#!/usr/bin/python

### create-pkgdb.py <file-list> <packages-dir>

import glob, sqlite, sys, re, os, string, shutil
import darlib

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
                print 'Unknown distribution tag %s in filename %s' % (dist, filename),
		raise

def readfile(file, builder=None):
	rec = {
		'filename': os.path.basename(file),
		'parent': os.path.basename(os.path.dirname(file)),
		'builder': builder,
	}
	rec.update(re.search('(?P<name>[^/]+)-(?P<version>[\w\.]+)-(?P<release>[\w\.]+)\.(?P<arch>\w+).rpm$', file).groupdict())
	rec['repo'] = repo(file)
	if rec['arch'] in ('src', 'nosrc'): 
		rec['dist'] = rec['arch']
	else:
		rec['dist'] = dist(file)
	return rec

sys.stdout = os.fdopen(1, 'w', 0)

pkgcon, pkgcur = darlib.opendb('pkg', create=True)
#pkgcon.autocommit = 1

#list = []
#for arg in sys.argv[1:]:
#	if os.path.isfile(arg):
#		list += open(arg, 'r').readlines()
#	elif os.path.isdir(arg):
#		list += glob.glob(os.path.join(arg, '*/*.rpm'))
#
#if not list:
#	list += glob.glob(os.path.join(packagedir, '*/*.rpm'))

for builder in ('dag', 'dries'):
	try:
		list = open('/dar/pub/rpmforge/persona/'+builder+'/packagelist-'+builder+'.txt', 'r').readlines()
	except:
		import urllib2
		req = urllib2.Request('http://apt.sw.be/rpmforge/persona/'+builder+'/packagelist-'+builder+'.txt')
		list = urllib2.urlopen(req).readlines()

	for file in list:
		try:
			pkgrec = readfile(file, builder)
		except:
#			print file, 'FAILED'
			continue
		darlib.insertdb(pkgcur, 'pkg', pkgrec)
pkgcon.commit()
