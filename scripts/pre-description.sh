#!/bin/bash

### This script adds an RPMforge banner to the description of the package.

#echo "** pre-svn-rev: OrigSpecfile: $origspecfile, Specfile: $specfile"
#set -x

#perl -pi.orig -0 -e 's|\n%changelog\n(\*\s.+)\n|\n%changelog\n$1 - '$revision'/'$author'\n|' $specfile
#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - 
# This package is part of the RPMforge community project. In case you have
# an improvement or feedback about this package, please visit:
#
# 		http://rpmforge.net/user/package/$app/
#
# The person responsible for this package is:
#
#		http://rpmforge.net/developer/team/$author/

#diff -u "$specfile".orig "$specfile"
#set +x
