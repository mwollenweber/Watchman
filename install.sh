#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# For OSX development
if [[ `uname` == "Darwin" ]]; then
    script_directory=$(dirname "$0")

    brew update
    echo "Installing Postgres"
    brew install postgresql
    brew services start postgresql
    echo "Installing Redis"
    brew install redis
    brew services start redis

else
    script_directory=$(dirname $(readlink -f $BASH_SOURCE))

    apt-get update
    apt-get install screen git gh python3 virtualenv postgresql-all redis
    service postgresql start
    service redis start
fi

source $script_directory/config.rc
sudo -u postgres createdb $DBNAME
sudo -u postgres psql -c "CREATE USER $DBUSER WITH ENCRYPTED PASSWORD '$DBPASSWORD';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DBNAME to $DBUSER;"
sudo -u postgres psql -c "ALTER DATABASE $DBNAME OWNER TO $DBUSER;"

mkdir $script_directory/tmp
virtualenv env
source env/bin/activate
pip install -r requirements
python manage.py makemigrations
python manage.py migrate
python manage.py init_zones
python manage.py enable_zones tech technology security gov
python manage.py createsuperuser

