#!/bin/bash

### This script adds the last change author and revision to the
### changelog of the SPEC file, so RPM packages include it.

script="pre-svn-rev"

if [ -z "$origspecfile" -o -z "$specfile" ]; then
        echo "** $script: Variable \$origspecfile or \$specfile is not set. Disabling $script." >&2
        return 0
fi

#echo "** $script: OrigSpecfile: $origspecfile, Specfile: $specfile"; set -x

### Get Author and Revision from original specfile
info="$(svn info $origspecfile 2>/dev/null)"
if [ -z "$info" ]; then
	echo "** $script: No SVN info found. Please commit this SPEC file." >&2
	return 0
fi

author="$(echo "$info" | grep -E '^Last Changed Author: ' | sed -e 's|Last Changed Author: ||')"
revision="$(echo "$info" | grep -E '^Last Changed Rev: ' | sed -e 's|Last Changed Rev: ||')"

changed=""
if [ "$(svn diff "$origspecfile")" ]; then
	changed="+"
fi

#echo "** $script: Author: $author, Revision: $revision, Changed: $changed"

### Add Revision and Author to specfile
perl -pi.orig -0 -e 's|\n%changelog\n(\*\s.+)\n|\n%changelog\n$1 - '$revision$changed'/'$author'\n|' $specfile

#set +x; diff -u "$specfile".orig "$specfile"
