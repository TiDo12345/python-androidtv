#!/bin/bash

# Make sure there is only 1 argument passed
if [ "$#" -ne 1 ]; then
    echo "You must provide a new version"
    exit 1
fi

# Make sure the new version is not empty
if [ -z "$1" ]; then
    echo "You must provide a non-empty version"
    exit 1
fi

# get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# get the package name
PACKAGE=$($DIR/get_package_name.sh)

# get the current version
VERSION=$($DIR/get_version.sh)

# Announce the version bump
echo "Bumping the version from $VERSION to $1"

# __init__.py
sed -i "s|__version__ = \"$VERSION\"|__version__ = \"$1\"|g" $DIR/../$PACKAGE/__init__.py

# pyproject.toml and docs/source/conf.py read the version from __init__.py
