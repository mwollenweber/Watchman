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
echo "Installing Postgres"
brew install postgresql
brew services start postgresql

echo "Installing Redis"
brew install redis
brew services start redis
createuser postgres
createdb watchman

echo "DONE"