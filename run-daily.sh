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


python manage.py update_zone `echo $ENABLED_ZONES`
python manage.py run_searches
python manage.py run_alerts
find ./tmp/*.txt  -mtime +30d  -type f  -exec rm {} \;