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
9. python manage.py migrate
10. python manage.py init_zones
11. python manage.py firstload_zonefile <zone> #repeat for zones you want to watch
12. Enable zones in zonelist
