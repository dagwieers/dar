#!/usr/bin/python

### This python scripts lists all the available
### Perl modules based on CPAN information.

import sys, os, time, getopt, urllib2, gzip, re, yaml, tarfile, rpm, types
import cElementTree as ElementTree

tmppath = "/var/tmp"

### FIXME: Create own version comparison instead of using RPM's
def vercmp(v1, v2):
    return rpm.labelCompare((None, v1, None), (None, v2, None))

def download(url):
    filename = os.path.join(tmppath, os.path.basename(url))
    try:
        st = os.stat(filename)
        if st and st.st_mtime + 1800 > time.time():
#            print >>sys.stderr, "File %s is recent, skip download." % os.path.basename(url)
            return True
    except:
        pass
    try:
        req = urllib2.Request(url)
        fdin = urllib2.urlopen(req)
    except:
#        print >>sys.stderr, "Failed to download file from %s" % url
        return False
    fdout = open(filename, 'w')
    fdout.write(fdin.read())
    fdin.close()
    fdout.close()
    return True

def check_version(module, version):
    specfile = os.path.join('perl-'+module, 'perl-'+module+'.spec')
    if os.path.isfile(specfile):
        specversion = None
        for line in open(specfile):
            if line.startswith('Version: '):
                specversion = line.split('Version: ')[-1].strip()
        if not specversion:
            print >>sys.stderr, "Error: file %s does not contain a version ??" % specfile
        if listnew and vercmp(version, specversion) > 0:
            print 'perl-'+module, specversion, version
    else:
#        print >>sys.stderr, "Error: file %s not found." % specfile
        pass

listall = False
listnew = False
listmissing = False

args = sys.argv[1:]
try:
    opts, args = getopt.getopt (args, 'ahmnv',
        ['all', 'help', 'missing', 'new', 'version'])
except getopt.error, exc:
    print >>sys.stderr, 'dar-list-perl: %s, try dar-list-perl.py -h for a list of all the options' % str(exc)
    sys.exit(1)

for opt, arg in opts:
    if opt in ['-h', '--help']:
        pass
    elif opt in ['-v', '--version']:
        pass
    elif opt in ['-a', '--all']:
        listall = True
    elif opt in ['-m', '--missing']:
        listmissing = True
    elif opt in ['-n', '--new']:
        listnew = True

if not listall and not listnew and not listmissing:
    print >>sys.stderr, 'dar-list-perl: You have to at least add a flag.'
    sys.exit(2)

### Download latest package list from CPAN
download('ftp://ftp.kulnet.kuleuven.ac.be/pub/mirror/CPAN/modules/02packages.details.txt.gz')

modules = {}

fd = gzip.open('/var/tmp/02packages.details.txt.gz', 'r')
for line in fd.readlines():
    pinfo = line.split()
    if len(pinfo) < 3: continue
    pkgversion = pinfo[1]
    pkglocation = pinfo[2]

    file = os.path.basename(pkglocation)
    l = file.split('-')

    module = '-'.join(l[0:-1])

    version = l[-1]
    if version.endswith('.tar.gz'):
        version = version.split(".tar.gz")[0]
    elif version.endswith('.tgz'):
        version = version.split(".tgz")[0]
    elif version.endswith('.zip'):
        version = version.split(".zip")[0]
    if version.startswith('v'):
        version = version[1:]

    if module not in modules.keys():
        modules[module] = version
        if listnew:
            check_version(module, version)
    elif version != modules[module]:
#        print "Package %s has 2 versions. (%s != %s)" % (module, modules[module], version)
        if version > modules[module]:
            modules[module] = version
            if listnew:
                check_version(module, version)

if listall:
#    modules.sort()
    for module in modules:
        print module, modules[module]

if listmissing:
#    modules.sort()
    for module in modules:
        if not os.path.isfile(os.path.join('perl-'+module, 'perl-'+module+'.spec')):
            print module, modules[module]

sys.exit(0)
