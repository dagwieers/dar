#!/bin/bash

#echo "Specfile: $NEWSPECFILE"
#set -x

AUTHOR="$(grep '^# Authority: ' $NEWSPECFILE | sed -e 's|^# Authority: ||')"

case "$AUTHOR" in
	(dries)
		PACKAGER="Dries Verachtert <dries\@ulyssis.org>"
		;;
	(bert)
		PACKAGER="Bert de Bruijn <bert\@debruijn.be>"
		;;
	(dag|thias|matthias|*)
		PACKAGER="Dag Wieers <dag\@wieers.com>"
		;;
esac

VENDOR="Dag Apt Repository, http://dag.wieers.com/apt/"

perl -pi.orig -e 's|^(Source:.+)$|Packager: '"$PACKAGER"'\nVendor: '"$VENDOR"'\n\n$1|' "$NEWSPECFILE"

#set +x
#diff -u "$NEWSPECFILE".orig "$NEWSPECFILE"
