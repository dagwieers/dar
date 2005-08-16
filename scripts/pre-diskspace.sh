#!/bin/bash

### This script checks if you have at least 20MB of diskspace free.

script="pre-diskspace"

if [ -z "$builddir" ]; then
	echo "** $script: Variable \$builddir is not set. Disabling $script." >&2
	return 0
fi

#echo "** pre-diskspace: Builddir: $builddir"; set -x

export free="$(set -- $(df $chrootdir/$builddir | grep -v 'Filesystem'); echo $4)"

while [ -z "$free" -o $free -lt 20480 ]; do
	echo "Disk is almost full ($free kB), please free up space in $builddir and press ENTER." >&2
	read a
	export free="$(set -- $(df $chrootdir/$builddir | grep -v 'Filesystem'); echo $4)"
done

#set +x
