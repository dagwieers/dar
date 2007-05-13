#!/usr/bin/python

### This python scripts automatically generates an RPMforge SPEC file
### for Perl modules based on CPAN information.

### Example modules:
###	perl-Tree-Simple		tests META.yml
###	perl-Tree-Simple-Visitor	tests sub-modules
###	perl-Kwiki			tests perl Buildrequires epoch

### More documentation about:
###	META.yml			http://module-build.source-forge.net/META-spec-current.html

import sys, os, time, getopt, urllib2, gzip, re, yaml, tarfile, rpm, types
import cElementTree as ElementTree

args = sys.argv[1:]
try:
	logname = os.getlogin()
except:
	logname = 'dag'
debug = False
noarch = True
realversion = None
authors = []
email = ''
tmppath = '/var/tmp'
license = ''

### Files considered a document:
### Announce ANNOUNCE Artistic ARTISTIC Artistic.txt AUTHORS Bugs BUGS
### Changelog ChangeLog CHANGELOG Changes CHANGES Changes.pod CHANGES.TXT
### Copying COPYING COPYRIGHT Credits CREDITS CREDITS.txt FAQ GNU_GPL.txt
### GNU_LGPL.txt GNU_LICENSE HACKING HISTORY INFO INSTALL INSTALLING
### INSTALL.txt LICENCE LICENSE MANIFEST META.yml NEWS NOTES NOTICE
### PORTING readme README readme.txt README.txt README.TXT RELEASE_NOTES
### SIGNATURE THANKS TODO UPGRADE VERSION *.txt  

docfiles = ('^ANNOUNCE', '^Artistic', '^AUTHORS', '^BUGS', '^ChangeLog',
	 '^Changes', '^Changes.pod', '^COPYING', '^COPYRIGHT', '^CREDITS',
	'^FAQ', '^GNU_LICENSE', '^HACKING', '^HISTORY', '^INFO', '^INSTALL',
	'^INSTALLING', '^LICENCE', '^LICENSE', '^MANIFEST', '^META.yml',
	'^NEWS', '^NOTES', '^NOTICE', '^PORTING', '^README', '^RELEASE_NOTES',
	'^SIGNATURE', '^THANKS', '^TODO', '^UPGRADE', '^VERSION', '^[^/]+.txt$')

authorities = {
	'dag': 'Dag Wieers <dag@wieers.com>',
	'dries': 'Dries Verachtert <dries@ulyssis.org>',
}

licenses = {
	'perl': 'Artistic/GPL',
}

### FIXME: Add proper epochs to perl-dependencies
epochs = ( '5.0.0', '5.6.1', '5.8.0', '5.8.5', '5.8.8' )

def download(url):
	filename = os.path.join(tmppath, os.path.basename(url))
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

### FIXME: Create own version comparison instead of using RPM's
def vercmp(v1, v2):
        return rpm.labelCompare((None, v1, None), (None, v2, None))

def epochify(version):
	epoch = 0
	for e, v in enumerate(epochs):
		if vercmp(str(version), v) >= 0:
			epoch = e
	return '%s:%s' % (epoch, version)

try:
	opts, args = getopt.getopt (args, 'dhnv',
		['debug', 'help', 'version'])
except getopt.error, exc:
	print >>sys.stderr, 'dar-perl: %s, try dar-perl.py -h for a list of all the options' % str(exc)
	sys.exit(1)

for opt, arg in opts:
	if opt in ['-h', '--help']:
		pass
	elif opt in ['-v', '--version']:
		pass
	elif opt in ['-d', '--debug']:
		debug = True

if not args:
	print >>sys.stderr, 'You have to provide a module name.'
	sys.exit(1)

module = args[0]
module = module.replace('::', '-')
modparts = module.split('-')

if module.startswith('perl-'):
	modparts = modparts[1:]
	module = '-'.join(modparts)

pmodule = module.replace('-', '::')

### Download latest package list from CPAN
download('ftp://ftp.kulnet.kuleuven.ac.be/pub/mirror/CPAN/modules/02packages.details.txt.gz')

### Download latest authors list from CPAN
download('ftp://ftp.kulnet.kuleuven.ac.be/pub/mirror/CPAN/authors/00whois.xml')

### Find specific package in CPAN package list
fd = gzip.open(os.path.join(tmppath, '02packages.details.txt.gz'), 'r')
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
tree = ElementTree.ElementTree(file=os.path.join(tmppath, '00whois.xml'))
root = tree.getroot()
for elem in root.getiterator('{http://www.cpan.org/xmlns/whois}cpanid'):
	if mnemo == elem.find('{http://www.cpan.org/xmlns/whois}id').text:
		authorel = elem.find('{http://www.cpan.org/xmlns/whois}fullname')
		emailel = elem.find('{http://www.cpan.org/xmlns/whois}email')
		try:
			author = "%s <%s>" % (authorel.text, emailel.text.replace('@','$').replace('.',','))
		except:
			break

		authors.append(author.encode('utf8', 'replace'))
		break

### Get the correct version from the source distribution
sdistname = "%s-%s.tar.gz" % (module, version)
cdistname = os.path.basename(location)
if sdistname != cdistname:
	realversion = version
	### FIXME: Get the version from the cdistname
	m = re.match('[^\d]+([\d\.]+).tar.gz', cdistname)
	if m:
	        l = m.groups()
		version = l[0]

### Try to download distribution
archive = os.path.join(tmppath, cdistname)
if os.path.isfile(archive):
	 os.remove(archive)
source = "http://www.cpan.org/modules/by-module/%s/%s" % (modparts[0], cdistname)
download(source)
if not os.path.isfile(archive):
	source = "http://www.cpan.org/authors/id/%s" % location
	download(source)

### Add %{version} and %{real_version} to source
source = source.replace(version, '%{version}')
if realversion:
	source = source.replace(realversion, '%{real_version}')

### Create basedir out of cdistname
basedir = cdistname.replace('.tar.gz', '')
basedir = basedir.replace(version, '%{version}')
if realversion:
	basedir = basedir.replace(realversion, '%{real_version}')
basedir = basedir.replace(module, '%{real_name}')

if realversion == 'undef':
	print >>sys.stderr, 'Version is undefined. Distribution %s is not a module.' % module
	sys.exit(1)

### Inspect distribution and extract information (%doc, META.yml, arch/noarch)
distfd = tarfile.open(archive, 'r:gz')
### Remove .tar.gz from base (Name-Version)
base = os.path.basename(archive)
l = base.split('.tar.gz')
base = l[0]
docs = []
meta = {}
for file in distfd.getnames():
	### Remove Name-Version/ from filename
	l = file.split(base+'/')
	shortfile = l[1]

	### Check if this is a noarch or arch package
	if file.endswith('.c') or file.endswith('.h') or file.endswith('.cc') or file.endswith('.xs'):
		noarch = False

	### Create %docs list
	for docre in docfiles:
		if re.search(docre, shortfile, re.I):
			docs.append(shortfile)

	### Parse META.yml (http://module-build.source-forge.net/META-spec-current.html)
	if shortfile == 'META.yml':
		member = distfd.getmember(file)
		meta = yaml.load(distfd.extractfile(member).read())
		if debug:
			print >>sys.stderr, 'META.yml contains the following info:'
			for key in meta.keys():
				print >>sys.stderr, '   %s: %s' % (key, meta[key])

docs.sort()

if os.path.isfile(archive):
	os.remove(archive)

### Compare deducted information with META.yml
if meta.has_key('name') and meta['name'] != module:
	print >>sys.stderr, 'Module %s is part of distribution %s. Please us that instead.' % (module, meta['name'])
	sys.exit(1)

if meta.has_key('version') and str(meta['version']) != version:
	print >>sys.stderr, 'Module %s has version mismatch between archive (%s) and META.yml (%s).' % (module, version, meta['version'])

if meta.has_key('type') and meta['type'] != 'module':
	print >>sys.stderr, 'Distribution %s is not a module.' % module
	sys.exit(1)

if meta.has_key('author'):
	authors = []
        if isinstance(meta['author'], types.StringType):
		author = meta['author'].replace('@','$').replace('.',',')
		authors.append(meta['author'].encode('utf8', 'replace'))
	elif isinstance(meta['author'], types.ListType):
		for author in meta['author']:
			author = author.replace('@','$').replace('.',',')
			authors.append(author.encode('utf8', 'replace'))

if meta.has_key('license') and meta['license'] in licenses.keys():
	license = licenses[meta['license']]
else:
	artistic = False
	gpl = False
	lgpl = False
	for doc in docs:
		if doc in ('Artistic', 'ARTISTIC', 'Artistic.txt'):
			artistic = True
		if doc in ('Copying', 'COPYING', 'GNU_GPL.txt', 'GNU_LICENSE'):
			gpl = True
		if doc in ('GNU_LGPL.txt'):
			lgpl = True
	if artistic:
		license = 'Artistic'
	if gpl:
		if license: license = license + '/'
		license = license + 'GPL'
	if lgpl:
		if license: license = license + '/'
		license = license + 'LGPL'
	if not license:
		license = 'Artistic/GPL'
		print >>sys.stderr, 'License could not be determined.'

if meta.has_key('abstract'):
	summary = "%s" % meta['abstract']
	description = "%s." % meta['abstract']
else:
	summary = "Perl module named %s" % module
	description = "perl-%s is a Perl module." % module
	print >>sys.stderr, 'No abstract found.'

if meta.has_key('build_requires') and meta['build_requires'] and meta['build_requires'].has_key('perl-Inline'):
	noarch = False
if meta.has_key('requires') and meta['requires'] and meta['requires'].has_key('perl-Inline'):
	noarch = False

if debug:
	print >>sys.stderr, module, version, "perl-%s/perl-%s.spec" % (module, module)
	if noarch:
		print >>sys.stderr, 'noarch package'
	else:
		print >>sys.stderr, 'arch package'
	if realversion:
		print >>sys.stderr, 'source has different version format than CPAN (%s vs %s)' % (version, realversion)
	print >>sys.stderr, 'Found following docs:', ' '.join(docs)
	print >>sys.stderr, 'Distribution archive %s contains:' % cdistname
	for file in distfd.getnames():
		print >>sys.stderr, '  ', file

print '# $Id$'
print '# Authority:', logname

for author in authors:
	print "# Upstream: %s" % author
print
print '%define perl_vendorlib %(eval "`%{__perl} -V:installvendorlib`"; echo $installvendorlib)'
print '%define perl_vendorarch %(eval "`%{__perl} -V:installvendorarch`"; echo $installvendorarch)'
print
print '%define real_name', module

if realversion:
	print '%define real_version', realversion
	
print

print "Summary: %s" % summary
print "Name: perl-%s" % module
print 'Version:', version
print 'Release: 1'

print 'License: %s' % license
print 'Group: Applications/CPAN'
print "URL: http://search.cpan.org/dist/%s/" % module
print
print "Source: %s" % source
print 'BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root'
print

if noarch:
	print "BuildArch: noarch"

### FIXME: Add BuildRequires from Makefile.PL
if meta.has_key('requires') and meta['requires'] and meta['requires'].has_key('perl'):
	print "BuildRequires: perl >= %s " % epochify(meta['requires']['perl'])
else:
	print "BuildRequires: perl"

### Requires are extracted by RPM itself
#print "Requires: perl"
#if meta.has_key('requires'):
#	for key in meta['requires']:
#		if meta['requires'][key]:
#			print "Requires: perl(%s) >= %s" % (key, meta['requires'][key])
#		else:
#			print "Requires: perl(%s)" % key

if meta.has_key('build_requires'):
	for key in meta['build_requires']:
		if meta['build_requires'][key]:
			print "BuildRequires: perl(%s) >= %s" % (key, meta['build_requires'][key])
		else:
			print "BuildRequires: perl(%s)" % key
if meta.has_key('conflicts'):
	for key in meta['conflicts']:
		print "Conflict: perl(%s)" % key
print

print "%description"
print description
print
print "%prep"
print "%%setup -n %s" % basedir
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
		print '%%{perl_vendorlib}/%s.pm' % modparts[0]
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
