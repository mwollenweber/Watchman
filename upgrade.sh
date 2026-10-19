#!/bin/bash
# Everything is inside main so bash reads the whole script before running it;
# git pull may rewrite this file mid-run.

main() {
    if [ $# -eq 0 ]
      then
        echo "Sourcing config.rc"
        source config.rc
      else
        echo "Sourcing $1"
        source $1
    fi

    # Stop at the first failure so migrations don't run against a broken install
    set -e

    git pull
    source ./python-env.sh
    ensure_env
    source ./env/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    python manage.py makemigrations
    python manage.py migrate
}

main "$@"
exit
