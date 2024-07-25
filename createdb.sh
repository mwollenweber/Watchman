#!/bin/bash

# For OSX development
if [[ `uname` == "Darwin" ]]; then
    script_directory=$(dirname "$0")
fi

if [ -e $script_directory/config.rc ]
then
	source $script_directory/config.rc
else
	echo "WARN: $script_directory/config.rc does not exist."
fi

brew update
brew install postgresql
brew services start postgresql
createuser postgres
createdb watchman
