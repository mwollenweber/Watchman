#!/bin/bash



source config.rc
source ./env/bin/activate
git pull
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
