#!/bin/bash

### This script adds the last change author and revision to the
### changelog of the SPEC file, so RPM packages include it.

#echo "** pre-svn-rev: OrigSpecfile: $origspecfile, Specfile: $specfile"
#set -x

### Get Author and Revision from original specfile
info=""; author=""; revision=""

info="$(svn info $origspecfile 2>/dev/null)"
if [ -z "$info" ]; then
	echo "** pre-svn-rev: No SVN info found. Please commit this SPEC file." >&2
	exit 0
fi

author="$(echo "$info" | grep -E '^Last Changed Author: ' | sed -e 's|Last Changed Author: ||')"
revision="$(echo "$info" | grep -E '^Last Changed Rev: ' | sed -e 's|Last Changed Rev: ||')"

#echo "** pre-svn-rev: Author: $author, Revision: $revision"

### Add Revision and Author to specfile
perl -pi.orig -0 -e 's|\n%changelog\n(\*\s.+)\n|\n%changelog\n$1 - '$revision'/'$author'\n|' $specfile

#diff -u "$specfile".orig "$specfile"
#set +x
