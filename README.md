# Watchman
Watchman is a security tool that watches domains and fqdns. You can read more about it here: https://docs.google.com/presentation/d/10TtlZO01WfJo9raF-ShS06m5bak1NSG1/edit#slide=id.g324938c8159_1_85


## Setup
1. git clone https://github.com/mwollenweber/Watchman.git
2. cd Watchman
2. cp example-config.rc config.rc
3. nano config.rc
4. sudo ./install.sh

### Add a Client
- http://localhost:8000/admin/Watchman/client/add/

### Add a Search
- http://localhost:8000/admin/Watchman/search/add/
I add the domain - tld as a substring match and the domain+tld as str distance

### Add Alert Config
http://localhost:8000/admin/Watchman/alertconfig/



## Run a daily zone update + match + alerts
1. ./daily-run.sh 


## Other Commands
### Update a Specific Zone:
- python manage.py update_zone <zonename>



### See Search Results
- Browse to http://localhost:8000/hits/
