#!/bin/bash

### This scripts add the last change author and revision to the
### changelog of the SPEC file, so RPM packages include it.

#echo "** pre-svn-rev: OrigSpecfile: $origspecfile, Specfile: $specfile"
#set -x

### Get Author and Revision from original specfile
info=""; author=""; revision=""
set -- $(
while [ -z "$info" ]; do
	info="$(svn info $origspecfile 2>/dev/null)"
	if [ "$info" ]; then
		echo "$info" | grep -E '^Last Changed Author: ' | sed -e 's|Last Changed Author: ||'
		echo "$info" | grep -E '^Last Changed Rev: ' | sed -e 's|Last Changed Rev: ||'
		break
	else
		sleep 5
	fi
done
)
author="$1"; revision="$2"

#echo "** pre-svn-rev: Author: $author, Revision: $revision"

### Add Revision and Author to specfile
perl -pi.orig -0 -e 's|\n%changelog\n(\*\s.+)\n|\n%changelog\n$1 - '$revision'/'$author'\n|' $specfile

#diff -u "$specfile".orig "$specfile"
#set +x
