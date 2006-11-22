#!/bin/bash

### This script intervenes when a release tag conforms to the new scheme (has .2)

script="pre-new-release"
release_regex="\b\.2$"

if [ -z "$force" ] && [ "$disttag" != "fc5" -a "$disttag" != "fc6" -a "$disttag" != "el5" ] && echo $release | grep -q -E "$release_regex"; then
	echo "** $script: Not building $app for $disttag/$arch since $release matches new release scheme."
	continue 2
fi

#echo "** $script: App: $app, Release: $release"
