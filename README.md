# Watchman

Watchman is a security tool that watches domains and fqdns

## Setup

1. git 
2. cp example-config.rc config.rc
3. emacs config.rc
4. sudo install.sh
5. python manage.py enable_zone app bbc biz blog careers cheap data docs email eus gov inc info jobs java kosher law llc link lol mov net new one online org page pay  pics pro run security sucks team tech technology tel top xyz vip zip com



## Update a Specific Zone:
1. source env/bin/activate && source config.rc
2. python manage.py update_zone <zonename>

## Create Searches
1. Browse to http://localhost:8000/admin/Watchman/search/
2. Add relevant clients and searches
 
## Manually Run Searches (Stored in DB):
1. source env/bin/activate && source config.rc
2. python manage.py run_searches 

## See Search Results
1. Browse to http://localhost:8000/hits/

