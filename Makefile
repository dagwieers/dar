name=dar
description=Dag Apt Repository builder
version=0.6.0
arch=noarch

prefix=/usr
datadir=/usr/share
sysconfdir=/etc
localstatedir=/var
libdir=/usr/lib
sbindir=/usr/sbin

DIST_SCRIPTS=dar-build dar-dotty dar-exec dar-kickoff dar-prepare dar-sync dar-update
DIST_LIBS=dar-functions compartment.sh

DESTDIR=

#include Functions.mk

all: check

check:
	@echo "Syntax checking source-files."; \
	for i in dar.conf $(DIST_SCRIPTS) $(DIST_LIBS); do bash -n $$i || exit 1; done

install:
	install -m0755 -d $(DESTDIR)$(sysconfdir)/dar/{config,dists} \
		$(DESTDIR)$(sysconfdir)/logrotate.d \
		$(DESTDIR)$(datadir)/dar/skel \
		$(DESTDIR)$(libdir)/dar \
		$(DESTDIR)$(sbindir)
	install -m0700 -d $(DESTDIR)$(localstatedir)/log/dar

	install -m0644 dar.conf $(DESTDIR)$(sysconfdir)/dar

	install -m0755 $(DIST_SCRIPTS) $(DESTDIR)$(sbindir)
	install -m0755 $(DIST_LIBS) $(DESTDIR)$(libdir)/dar/
#	install -m0644 dists/*/* $(DESTDIR)$(sysconfdir)/dar/dists/
	cp -af dists/* $(DESTDIR)$(sysconfdir)/dar/dists/

#	install -m0644 skel/* $(DESTDIR)$(datadir)/dar/skel/
	cp -af skel/* $(DESTDIR)$(datadir)/dar/skel/
