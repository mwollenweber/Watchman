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
git pull
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
