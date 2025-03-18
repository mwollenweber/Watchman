#!/bin/bash

source ./config.rc

# For OSX development
if [[ `uname` == "Darwin" ]]; then
    brew update
    echo "Installing Postgres"
    brew install postgresql
    brew services start postgresql
    echo "Installing Redis"
    brew install redis
    brew services start redis

    createdb $DBNAME
    psql $DBNAME -c  "CREATE USER $DBUSER WITH ENCRYPTED PASSWORD '$DBPASSWORD';"
    psql $DBNAME -c "GRANT ALL PRIVILEGES ON DATABASE $DBNAME to $DBUSER;"
    psql $DBNAME -c "ALTER DATABASE $DBNAME OWNER TO $DBUSER;"

else
    sudo apt update
    sudo apt install screen git gh python3 virtualenv postgresql-all redis
    sudo service postgresql start
    sudo service redis start

    sudo -u postgres createdb $DBNAME
    sudo -u postgres psql -c "CREATE USER $DBUSER WITH ENCRYPTED PASSWORD '$DBPASSWORD';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DBNAME to $DBUSER;"
    sudo -u postgres psql -c "ALTER DATABASE $DBNAME OWNER TO $DBUSER;"

fi


mkdir ./tmp
virtualenv env
source env/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py init_zones
python manage.py enable_zone `echo $ENABLED_ZONES`
echo "Create a Super User"
python manage.py createsuperuser
echo "Install Complete"
echo "To run a daily update launch ./run-daily.sh"
