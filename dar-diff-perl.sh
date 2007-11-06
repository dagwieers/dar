#!/bin/bash

for pkg in $*; do
    if [ ! -f /dar/rpms/$pkg/$pkg.spec ]; then
        echo "SPEC file /dar/rpms/$pkg/$pkg.spec does not exist, creating." >&2
        /dar/tools/dar/dar-perl.py -c $pkg
        read
    else
        diff -u /dar/rpms/$pkg/$pkg.spec <(/dar/tools/dar/dar-perl.py $pkg) | cdiff | less -R -u
    fi
done
