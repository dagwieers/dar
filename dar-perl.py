#!/usr/bin/python

import sys, os, time

args = sys.argv[1:]
logname = os.getlogin()
noarch = False

try:
	import getopt
	opts, args = getopt.getopt (args, 'hnv',
		['help', 'noarch', 'version'])
except getopt.error, exc:
	print 'dar-perl: %s, try dstat -h for a list of all the options' % str(exc)
	sys.exit(1)

for opt, arg in opts:
	if opt in ['-h', '--help']:
		pass
	elif opt in ['-v', '--version']:
		pass
	elif opt in ['-n', '--noarch']:
		noarch = True

if args:
	module = args[0]
else:
	module = 'RPMforge-Template'

modparts = module.split('-')

#os.mkdir("/dar/rpms/%s" % module, "0755")

print '# $Id$'
print '# Authority:', logname

### FIXME: Get Author from CPAN
print '# Upstream:'
print
print '%define perl_vendorlib %(eval "`perl -V:installvendorlib`"; echo $installvendorlib)'
print '%define perl_vendorarch %(eval "`perl -V:installvendorarch`"; echo $installvendorarch)'
print
print '%define real_name ', module
print

### FIXME: Get Summary from CPAN
print 'Summary: '
print "Name: perl-%s" % module
print 'Version: '
print 'Release: 1'

### FIXME: Get License from CPAN
print 'License: Artistic'
print 'Group: Applications/CPAN'
print "URL: http://search.cpan.org/dist/%s/" % module
print
print "Source: http://www.cpan.org/modules/by-module/%s/%s-%%{version}.tar.gz" % (modparts[0], module)
print 'BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root'
print
if noarch:
	print "BuildArch: noarch"
print "BuildRequires: perl"
print "Requires: perl"
print

### FIXME: Get Description from CPAN
print "%description"
print "%s" % module
print
print "%prep"
print "%setup -n %{real_name}-%{version}"
print
print "%build"
if noarch:
	print '%{__perl} Makefile.PL PREFIX="%{buildroot}%{_prefix}" \ INSTALLDIRS="vendor"'
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
print '%doc Changes MANIFEST README TODO'
print '%doc %{_mandir}/man3/*.3pm*'
#print '%{_bindir}/dave'

if noarch:
	### Print directory entries (if any)
	if modparts[:-1]:
		str = '%dir %{perl_vendorlib}/'
		for nr, part in enumerate(modparts[:-1]):
			str = str + "%s/" % modparts[nr]
			print str

	### Print module directory
	str = '%{perl_vendorlib}/'
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
	for nr, part in enumerate(modparts):
		str = str + "%s/" % modparts[nr]
	print str

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
print '%s Dag Wieers <dag@wieers.com> -' % time.strftime('%a %b %d %Y', time.localtime())
print '- Initial package. (using DAR)'

sys.exit(0)
