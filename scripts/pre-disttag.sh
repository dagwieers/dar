#!/bin/bash

#set -x

### Processing disttag variable
DISTTAG="${DISTTAG// *}"

#echo "Specfile: $NEWSPECFILE"
#echo "Disttag: $DISTTAG"
#echo "Tag: $TAG"

### Originally in dar-build
#cat "$SPECFILE" | sed -e "s|\(Release: *.\+\)|\1.${DISTTAG// *}.$TAG|" >"$NEWSPECFILE"

perl -pi.orig -e 's|^(Release)\s*:\s+(.+)\s*$|$1: '$DISTTAG'.'$TAG'\n|' "$NEWSPECFILE"

#diff -u "$NEWSPECFILE".orig "$NEWSPECFILE"
#set +x
