#!/bin/bash

#echo "** pre-brand: Specfile: $specfile"
#set -x

author="$(grep '^# Authority: ' $specfile | sed -e 's|^# Authority: ||')"

case "$author" in
	(dries)
		packager="Dries Verachtert <dries\@ulyssis.org>"
		;;
	(bert)
		packager="Bert de Bruijn <bert\@debruijn.be>"
		;;
	(dag|thias|matthias|*)
		packager="Dag Wieers <dag\@wieers.com>"
		;;
esac

vendor="Dag Apt Repository, http://dag.wieers.com/apt/"

### Removing existing branding
perl -pi.orig -e 's/^(Packager|Vendor|Distribution):.+\n$//m' "$specfile"

### Add own branding
perl -pi.orig -e 's|^(Source:.+)$|Packager: '"$packager"'\nVendor: '"$vendor"'\n\n$1|' "$specfile"

#set +x
#diff -u "$specfile.orig" "$specfile"
