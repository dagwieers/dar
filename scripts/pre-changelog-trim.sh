#!/bin/bash

### This script trims the changelog to include only the 6 last entries.

script="pre-changelog-trim"
entry_nr="6"

if [ -z "$app" -o -a "$buildarch" -o -z "$specfile" ]; then
        echo "** $script: Variable \$app, \$buildarch or \$specfile is not set. Disabling $script." >&2
        return 0
fi

#echo "** $script: App: $app, Buildarch: $buildarch, Specfile: $specfile"; set -x

if [ "$buildarch" == "src" ]; then
	return 0
fi

### Trim changelog to $entr_nr entries
perl -pi.orig -0 -e 's|(\n%changelog)((\n\* .+?){'$entry_nr'})\n\* .+$|$1$2|sm' $specfile
if [ "$(diff -u "$specfile".orig "$specfile")" ]; then
	echo -e "- ...\n- Changelog trimmed, see http://svn.rpmforge.net/svn/trunk/rpms/$app/$app.spec" >>$specfile
fi

#set +x; diff -u "$specfile".orig "$specfile"
