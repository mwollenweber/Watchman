#!/bin/bash


script_directory=$(dirname $(readlink -f $BASH_SOURCE))


if [ -e $script_directory/config.rc ]
then
	source $script_directory/config.rc
else
	echo "WARN: $script_directory/config.rc does not exist."
fi

exec $script_directory/env/bin/celery -A Watchman beat -l DEBUG