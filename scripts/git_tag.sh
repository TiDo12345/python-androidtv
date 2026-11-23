#!/bin/bash

# get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# get the current version
VERSION=$($DIR/get_version.sh)


# Announce the tag
echo "Creating tag v$VERSION"

cd $DIR/..
git tag -a "v$VERSION" -m "v$VERSION"
echo "Push it with: git push <remote> refs/tags/v$VERSION (GitHub Actions then builds the release)"
