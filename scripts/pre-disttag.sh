#!/bin/bash

#echo "Specfile: $NEWSPECFILE, Disttag: $DISTTAG, Tag: $TAG"
#set -x

case "$ARCH" in
	(src)
		perl -pi.orig -e 's|^(Release)\s*:\s+(.+)\s*$|$1: $2.'$TAG'\n|' "$NEWSPECFILE"
		;;
	(*)
		perl -pi.orig -e 's|^(Release)\s*:\s+(.+)\s*$|$1: $2.'${DISTTAG// *}'.'$TAG'\n|' "$NEWSPECFILE"
		;;
esac

#diff -u "$NEWSPECFILE".orig "$NEWSPECFILE"
#set +x
