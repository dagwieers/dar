#!/usr/bin/python

import sys, os, time, getopt, urllib2, gzip, re
import cElementTree as ElementTree
import tarfile

args = sys.argv[1:]
logname = os.getlogin()
debug = False
noarch = True
realversion = None

docfiles = ('Announce', 'ANNOUNCE', 'Artistic', 'ARTISTIC', 'Artistic.txt', 'AUTHORS', 'Bugs', 'BUGS', 'Changelog', 'ChangeLog', 'CHANGELOG', 'Changes', 'CHANGES', 'Changes.pod', 'CHANGES.TXT', 'Copying', 'COPYING', 'COPYRIGHT', 'Credits', 'CREDITS', 'CREDITS.txt', 'FAQ', 'GNU_GPL.txt', 'GNU_LGPL.txt', 'GNU_LICENSE', 'HACKING', 'HISTORY', 'INFO', 'INSTALL', 'INSTALLING', 'INSTALL.txt', 'LICENCE', 'LICENSE', 'MANIFEST', 'META.yml', 'NEWS', 'NOTES', 'NOTICE', 'PORTING', 'readme', 'README', 'readme.txt', 'README.txt', 'README.TXT', 'RELEASE_NOTES', 'SIGNATURE', 'THANKS', 'TODO', 'UPGRADE', 'VERSION', '.txt')

authorities = {
	'dag': 'Dag Wieers <dag@wieers.com>',
	'dries': 'Dries Verachtert <dries@ulyssis.org>',
}

def download(url):
	filename = os.path.join('/dar/tmp', os.path.basename(url))
	if not os.path.exists(filename):
		try:
			req = urllib2.Request(url)
			fdin = urllib2.urlopen(req)
		except:
			return
		fdout = open(filename, 'w')
		fdout.write(fdin.read())
		fdin.close()
		fdout.close()

try:
	opts, args = getopt.getopt (args, 'dhnv',
		['debug', 'help', 'version'])
except getopt.error, exc:
	print 'dar-perl: %s, try dstat -h for a list of all the options' % str(exc)
	sys.exit(1)

for opt, arg in opts:
	if opt in ['-h', '--help']:
		pass
	elif opt in ['-v', '--version']:
		pass
	elif opt in ['-d', '--debug']:
		debug = True

if args:
	module = args[0]
else:
	module = 'RPMforge-Template'

if module.startswith('perl-'):
	l = module.split('-')
	module = '-'.join(l[1:])

modparts = module.split('-')
pmodule = '::'.join(modparts)

### Download latest package list from CPAN
download('ftp://ftp.kulnet.kuleuven.ac.be/pub/mirror/CPAN/modules/02packages.details.txt.gz')

### Download latest authors list from CPAN
download('ftp://ftp.kulnet.kuleuven.ac.be/pub/mirror/CPAN/authors/00whois.xml')

### Find specific package in CPAN package list
fd = gzip.open('/dar/tmp/02packages.details.txt.gz', 'r')
for line in fd.readlines():
	pinfo = line.split()
	if len(pinfo) > 2 and pmodule == pinfo[0]:
		break
else:
	print >>sys.stderr, 'Module %s not found in CPAN.' % module
	sys.exit(1)
	
version = pinfo[1]
location = pinfo[2]

ppath = pinfo[2].split('/')
mnemo = ppath[2]

### Find specific author in CPAN authors list
tree = ElementTree.ElementTree(file='/dar/tmp/00whois.xml')
root = tree.getroot()
for elem in root.getiterator('{http://www.cpan.org/xmlns/whois}cpanid'):
	if mnemo == elem.find('{http://www.cpan.org/xmlns/whois}id').text:
		authorel = elem.find('{http://www.cpan.org/xmlns/whois}fullname')
		try:
			author = authorel.text
		except:
			author = ''

		emailel = elem.find('{http://www.cpan.org/xmlns/whois}email')
		try:
			email = emailel.text.replace('@','$').replace('.',',')
		except:
			email = ''
		break

### Get the correct version from the source distribution
sdistname = "%s-%s.tar.gz" % (module, version)
cdistname = os.path.basename(location)
if sdistname != cdistname:
	realversion = version
	### FIXME: Get the version from the cdistname
	m = re.match('.+-([\d\.]+).tar.gz', cdistname)
	if m:
	        l = m.groups()
		version = l[0]
#	print >>sys.stdout, "sdistname != cdistname"

### Try to download distribution
archive = os.path.join('/dar/tmp', cdistname)
download("http://www.cpan.org/modules/by-module/%s/%s" % (modparts[0], cdistname))
bymodule = True
if not os.path.exists(archive):
	download(location)
	bymodule = False

### Inspect distribution and extract information (%doc, META.yml, arch/noarch)
distfd = tarfile.open(archive, 'r:gz')
### Remove .tar.gz from base (Name-Version)
base = os.path.basename(archive)
l = base.split('.tar.gz')
base = l[0]
docs = []
for file in distfd.getnames():
	### Remove Name-Version/ from filename
	l = file.split(base+'/')
	shortfile = l[1]
	if file.endswith('.c') or file.endswith('.h') or file.endswith('.cc') or file.endswith('.xs'):
		noarch = False
	for docfile in docfiles:
		if shortfile == docfile:
			docs.append(shortfile)
	### Parse META.yml
#	if shortfile == 'META.yml':
#		member = distfd.getmember(file)
#		meta = distfd.extractfile(member)
#		for line in meta.readlines():
#			print >>sys.stderr, line
	### Parse README
#	if shortfile == 'README':
#		member = distfd.getmember(file)
#		meta = distfd.extractfile(member)
#		for line in meta.readlines():
#			print >>sys.stderr, line
docs.sort()

if debug:
	print >>sys.stderr, module, version, "perl-%s/perl-%s.spec" % (module, module)
	if noarch:
		print >>sys.stderr, 'noarch package by %s <%s>' % (author, email)
	else:
		print >>sys.stderr, 'arch package by %s <%s>' % (author, email)
	if realversion:
		print >>sys.stderr, 'source has different version format than CPAN (%s vs %s)' % (version, realversion)
	print >>sys.stderr, 'Found following docs:', ' '.join(docs)
	print >>sys.stderr, 'Distribution archive %s contains:' % cdistname
	for file in distfd.getnames():
		print >>sys.stderr, '  ', file

#print >>sys.stderr, "http://search.cpan.org/dist/%s/" % module

print '# $Id$'
print '# Authority:', logname

author = author.encode('utf8', 'replace') 
if email:
	print "# Upstream: %s <%s>" % (author, email)
else:
	print "# Upstream: %s" % author
print
print '%define perl_vendorlib %(eval "`%{__perl} -V:installvendorlib`"; echo $installvendorlib)'
print '%define perl_vendorarch %(eval "`%{__perl} -V:installvendorarch`"; echo $installvendorarch)'
print
print '%define real_name', module

if realversion:
	print '%define real_version', realversion
	
print

### FIXME: Get Summary from README in Archive
print "Summary: %s module for perl" % module
print "Name: perl-%s" % module
print 'Version:', version
print 'Release: 1'

### FIXME: Get License from Archive
print 'License: Artistic'
print 'Group: Applications/CPAN'
print "URL: http://search.cpan.org/dist/%s/" % module
print

if bymodule:
	print "Source: http://www.cpan.org/modules/by-module/%s/%s-%%{version}.tar.gz" % (modparts[0], module)
else:
	print "Source: http://www.cpan.org/authors/id/%s" % location

print 'BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root'
print

if noarch:
	print "BuildArch: noarch"

print "BuildRequires: perl"
#print "Requires: perl"
print

### FIXME: Get Description from README in Archive
print "%description"
print "%s module for perl." % module
print
print "%prep"
#if realversion:
#	print "%setup -n %{real_name}-%{real_version}"
print "%setup -n %{real_name}-%{version}"
print
print "%build"
if noarch:
	print '%{__perl} Makefile.PL INSTALLDIRS="vendor" PREFIX="%{buildroot}%{_prefix}"'
	print '%{__make} %{?_smp_mflags}'
else:
	print 'CFLAGS="%{optflags}" %{__perl} Makefile.PL INSTALLDIRS="vendor" PREFIX="%{buildroot}%{_prefix}"'
	print '%{__make} %{?_smp_mflags} OPTIMIZE="%{optflags}"'
print
print '%install'
print '%{__rm} -rf %{buildroot}'
print '%makeinstall'
print
print '### Clean up buildroot'
if noarch:
	print '%{__rm} -rf %{buildroot}%{perl_archlib} %{buildroot}%{perl_vendorarch}'
else:
	print '%{__rm} -rf %{buildroot}%{perl_archlib} %{buildroot}%{perl_vendorarch}/auto/*{,/*{,/*}}/.packlist'
print
print '%clean'
print '%{__rm} -rf %{buildroot}'
print

### FIXME: Create filelist based on test-build or source-tree ?
print '%files'
print '%defattr(-, root, root, 0755)'
### Check DOCS in archive from "grep -h '^%doc' /dar/rpms/perl*/perl*.spec | grep -v mandir | xargs -n 1 | sort | uniq"
print '%doc', ' '.join(docs)
print "%%doc %%{_mandir}/man3/%s.3pm*" % pmodule
print '#%doc %{_mandir}/man3/*.3pm*'

if noarch:
	### Print directory entries (if any)
	if modparts[:-1]:
		str = '%dir %{perl_vendorlib}/'
		for nr, part in enumerate(modparts[:-1]):
			str = str + "%s/" % modparts[nr]
			print str

	### Print module directory
	str = '#%{perl_vendorlib}/'
	for nr, part in enumerate(modparts):
		str = str + "%s/" % modparts[nr]
	print str

	### Print module
	if modparts[:-1]:
		str = '%{perl_vendorlib}/'
		for nr, part in enumerate(modparts[:-1]):
			str = str + "%s/" % modparts[nr]
		print str + "%s.pm" % modparts[-1]
else:
	### Print directory entries (if any)
	if modparts[:-1]:
		str = '%dir %{perl_vendorarch}/'
		for nr, part in enumerate(modparts[:-1]):
			str = str + "%s/" % modparts[nr]
			print str

	### Print module directory
	str = '%{perl_vendorarch}/'
	for nr, part in enumerate(modparts[:-1]):
		str = str + "%s/" % modparts[nr]
	print str + "%s.pm" % modparts[-1]

	### Print auto directory entries (if any)
	if modparts[:-1]:
		str = '%dir %{perl_vendorarch}/auto/'
		for nr, part in enumerate(modparts[:-1]):
			str = str + "%s/" % modparts[nr]
			print str

	### Print auto module directory
	str = '%{perl_vendorarch}/auto/'
	for nr, part in enumerate(modparts):
		str = str + "%s/" % modparts[nr]
	print str

print
print '%changelog'
print '* %s %s - %s-1' % (time.strftime('%a %b %d %Y', time.localtime()), authorities[logname], version)
print '- Initial package. (using DAR)'

sys.exit(0)
