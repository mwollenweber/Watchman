# Watchman
Watchman is a security tool that watches domains and fqdns

## Setup
1. git clone https://github.com/mwollenweber/Watchman.git
2. cd Watchman
2. cp example-config.rc config.rc
3. nano config.rc
4. sudo ./install.sh


## Update Specified Zones and Run Searches (Stored in DB):
1. ./daily-run.sh 


## Update a Specific Zone:
1. source env/bin/activate && source config.rc
2. python manage.py update_zone <zonename>


## Create Searches
1. Browse to http://localhost:8000/admin/Watchman/search/
2. Add relevant clients and searches


## See Search Results
1. Browse to http://localhost:8000/hits/
