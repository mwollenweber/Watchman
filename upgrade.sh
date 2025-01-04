#!/bin/bash

script_directory=$(dirname $(readlink -f $BASH_SOURCE))


if [ -e $script_directory/config.rc ]
then
	source $script_directory/config.rc
else
	echo "WARN: $script_directory/config.rc does not exist."
fi

source $script_directory/env/bin/activate
git pull
python manage.py makemigrations --merge
python manage.py migrate
