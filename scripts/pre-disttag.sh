#!/bin/bash

### This script add a disttag to the SPEC file so packages can be
### identified easier, are unique and don't have the macro clutter.

script="pre-disttag"

if [ -z "$buildarch" -o -z "$repotag" -o -z "$specfile" -o -z "$disttag" ]; then
        echo "** $script: Variable \$buildarch, \$repotag, \$specfile or \$disttag is not set. Disabling $script." >&2
        return 0
fi

#echo "** $script: BuildArch: $buildarch, Disttag: $disttag, Repotag: $repotag, Specfile: $specfile"; set -x

case "$buildarch" in
	(src)	perl -pi.orig -e 's|^(Release)\s*:\s+([^\s]+)\s*$|$1: $2.'$repotag'\n|' "$specfile" ;;
	(*)	perl -pi.orig -e 's|^(Release)\s*:\s+([^\s]+)\s*$|$1: $2.'${disttag// *}'.'$repotag'\n|' "$specfile" ;;
esac

#set +x; diff -u "$specfile".orig "$specfile"
