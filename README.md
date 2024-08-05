# Watchman

Watchman is a security operations tool that watches domains and fqdns

## Setup

1. Clone Project
2. virtualenv env
3. source env/bin/activate
4. pip install -r requirements
5. cp example-config.rc config.rc
6. emacs -nw config.rc
7. source config.rc
8. bash createdb.sh
9. python manage.py makemigrations
9. python manage.py migrate
10. python manage.py init_zones
11. python manage.py firstload_zonefile <zone> #repeat for zones you want to watch
12. python manage.py enable_zone <zone>




## Update a Specific Zone:
1. source env/bin/activate && source config.rc
2. python manage.py update_zone <zonename>


## Manually Run Searches (Stored in DB):
1. source env/bin/activate && source config.rc
2. python manage.py run_searches 

