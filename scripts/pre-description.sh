#!/bin/bash

### This script adds an RPMforge banner to the description of the package.

script="pre-description"

if [ -z "$origspecfile" -o -z "$specfile" ]; then
        echo "** $script: Variable \$origspecfile or \$specfile is not set. Disabling $script." >&2
        return 0
fi

#echo "** $script: OrigSpecfile: $origspecfile, Specfile: $specfile"; set -x

#perl -pi.orig -0 -e 's|\n%changelog\n(\*\s.+)\n|\n%changelog\n$1 - '$revision'/'$author'\n|' $specfile
#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# This package is part of the RPMforge community project. Please provide
# feedback or improvements at:
#
#		http://rpmforge.net/user/package/$app/

#diff -u "$specfile".orig "$specfile"; set +x
