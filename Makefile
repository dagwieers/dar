name=dar
description=Dag Apt Repository builder
version=0.6.0
arch=noarch

prefix=/usr
datadir=/usr/share
sysconfdir=/etc
localstatedir=/var
sbindir=/usr/sbin

DIST_SCRIPTS=dar-build dar-dotty dar-exec dar-kickoff dar-metadata dar-new dar-prepare dar-repo dar-shell dar-sync dar-update
DIST_LIBS=dar-functions

DESTDIR=

#include Functions.mk

all: check

check:
	@echo "Syntax checking source-files."; \
	for i in dar.conf $(DIST_SCRIPTS) $(DIST_LIBS); do bash -n $$i || exit 1; done

install: check
	install -m0755 -d $(DESTDIR)$(sysconfdir)/dar/{dists,scripts} \
		$(DESTDIR)$(sysconfdir)/logrotate.d \
		$(DESTDIR)$(datadir)/dar/skel \
		$(DESTDIR)$(sbindir)
	install -m0700 -d $(DESTDIR)$(localstatedir)/log/dar

	install -D -m0644 dar.conf $(DESTDIR)$(sysconfdir)/dar/dar.conf

	install -m0755 $(DIST_SCRIPTS) $(DESTDIR)$(sbindir)
	install -m0755 $(DIST_LIBS) $(DESTDIR)$(datadir)/dar/
#	install -m0644 dists/*/* $(DESTDIR)$(sysconfdir)/dar/dists/
	cp -af dists/* $(DESTDIR)$(sysconfdir)/dar/dists/
	cp -af scripts/* $(DESTDIR)$(sysconfdir)/dar/scripts/

#	install -m0644 skel/* $(DESTDIR)$(datadir)/dar/skel/
	cp -af skel/* $(DESTDIR)$(datadir)/dar/skel/
