#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "Sourcing config.rc"
    source config.rc
  else
    echo "Sourcing $1"
    source $1
fi

source ./env/bin/activate
python manage.py update_zone `echo $ENABLED_ZONES`
python manage.py run_searches
python manage.py run_alerts
python manage.py purge_new
find ./tmp/*.txt  -mtime +15 -type f  -exec rm {} \;
