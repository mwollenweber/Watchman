#!/bin/bash

# For OSX development
if [[ `uname` == "Darwin" ]]; then
    script_directory=$(dirname "$0")
fi

# For Linux production deployment
if [[ `uname` == "Linux" ]]; then
    script_directory=$(dirname $(readlink -f $BASH_SOURCE))
fi

if [ -e $script_directory/config.rc ]
then
	source $script_directory/config.rc
else
	echo "WARN: $script_directory/config.rc does not exist."
fi


python manage.py update_zone  app bbc biz blog careers cheap data docs email eus gov inc info jobs java kosher law llc link lol mov net new one online org page pay  pics pro run security sucks team tech technology tel top xyz vip zip com
python manage.py run_searches
python manage.py run_alerts
