#!/usr/bin/python

### This python scripts lists all the available
### Perl modules based on CPAN information.

import sys, os, time, getopt, urllib2, gzip, re, yaml, tarfile, rpm, types
import cElementTree as ElementTree

file = "/var/tmp/dar-perl-list-02packages.details.txt.gz"

def download(url):
    filename = "/var/tmp/dar-perl-list-%s" % os.path.basename(url)
    ### FIXME: Check if the files on disk are older than 1 day
#   if not os.path.exists(filename):
    if True:
        try:
            req = urllib2.Request(url)
            fdin = urllib2.urlopen(req)
        except:
            return
        fdout = open(filename, 'w')
        fdout.write(fdin.read())
        fdin.close()
        fdout.close()

### Download latest package list from CPAN
download('ftp://ftp.kulnet.kuleuven.ac.be/pub/mirror/CPAN/modules/02packages.details.txt.gz')

modules = []

fd = gzip.open('/var/tmp/dar-perl-list-02packages.details.txt.gz', 'r')
for line in fd.readlines():
    pinfo = line.split()
    if len(pinfo) < 3: continue
    version = pinfo[1]
    location = pinfo[2]

    file = os.path.basename(location)
    l = file.split('-')
    module = '-'.join(l[0:-1])

    if module not in modules:
        modules.append(module)
        print module

#modules.sort()
#for module in modules:

sys.exit(0)
