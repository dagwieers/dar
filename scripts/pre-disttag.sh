#!/bin/bash

### This script add a disttag to the SPEC file so packages can be
### identified easier, are unique and don't have the macro clutter.

#echo "** pre-disttag: BuildArch: $buildarch, Disttag: $disttag, Repotag: $repotag, Specfile: $specfile"
#set -x

case "$buildarch" in
	(src)
		perl -pi.orig -e 's|^(Release)\s*:\s+([^\s]+)\s*$|$1: $2.'$repotag'\n|' "$specfile"
		;;
	(*)
		perl -pi.orig -e 's|^(Release)\s*:\s+([^\s]+)\s*$|$1: $2.'${disttag// *}'.'$repotag'\n|' "$specfile"
		;;
esac

#diff -u "$specfile".orig "$specfile"
#set +x
