#!/bin/bash

source config.rc
source ./env/bin/activate
python manage.py update_zone `echo $ENABLED_ZONES`
python manage.py run_searches
python manage.py run_alerts
python manage.py purge_new
find ./tmp/*.txt  -mtime +15 -type f  -exec rm {} \;
