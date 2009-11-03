#!/bin/bash

### This script adds proper Packager and Vendor tags to the SPEC file
### so that the Source packages contains a branded SPEC file.

script="pre-brand"

if [ -z "$specfile" ]; then
        echo "** $script: Variable \$specfile is not set. Disabling $script." >&2
        return 0
fi

#echo "** $script: Specfile: $specfile"; set -x

author="$(grep '^# Authority: ' $specfile | sed -e 's|^# Authority: ||')"
vendor="Dag Apt Repository, http://dag.wieers.com/apt/"

case "$author" in
    (dries)
        packager="Dries Verachtert <dries\@ulyssis.org>" ;;
    (bert)
        packager="Bert de Bruijn <bert\@debruijn.be>" ;;
    (hadams)
        packager="Heiko Adams <info\@fedora-blog.de>" ;;
    (cmr)
        packager="Christoph Maser <cmr\@financial.com>" ;;
    (dag|thias|matthias|*)
        packager="Dag Wieers <dag\@wieers.com>" ;;
esac

### Removing existing branding and add own branding
perl -pi.orig -e 's/^(Packager|Vendor|Distribution):.+\n$//is' "$specfile"
perl -pi.orig -e 's|^(Source0?:.+)$|Packager: '"$packager"'\nVendor: '"$vendor"'\n\n$1|i' "$specfile"

#set +x; diff -u "$specfile.orig" "$specfile"
