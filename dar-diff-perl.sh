#!/bin/bash
DIRNAME="$(dirname $0)"

for pkg in $*; do
    if [ ! -f $pkg/$pkg.spec ]; then
        echo "SPEC file $pkg/$pkg.spec does not exist, creating." >&2
        $DIRNAME/dar-perl.py -c $pkg
        read
    else
        diff -u $pkg/$pkg.spec <($DIRNAME/dar-perl.py $pkg) | cdiff | less -R -u
    fi
done
