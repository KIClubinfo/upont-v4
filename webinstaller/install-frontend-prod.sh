#!/bin/sh -e

# install dependancies
/usr/local/bin/npm install

# compile files with webpack
npx webpack --env --mode production
