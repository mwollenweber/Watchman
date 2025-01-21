#!/bin/bash

script_directory=$(dirname $(readlink -f $BASH_SOURCE))

if [ -e $script_directory/config.rc ]
then
	source $script_directory/config.rc
else
	echo "WARN: $script_directory/config.rc does not exist."
fi


python manage.py update_zone `echo $ENABLED_ZONES`
python manage.py run_searches
python manage.py run_alerts
python manage.py purge_new
find $script_directory/tmp/*.txt  -mtime +15d  -type f  -exec rm {} \;
