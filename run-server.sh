#!/bin/bash

source config.rc
source ./env/bin/activate
python manage.py runserver
