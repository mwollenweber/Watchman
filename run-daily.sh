#!/bin/bash

usage() {
    echo "Usage: $0 [--shutdown] [config-file]"
    echo "  --shutdown   Shut down the system when the run finishes (must be run as root)"
}

SHUTDOWN=0
CONFIG=""
for arg in "$@"; do
    case "$arg" in
        --shutdown) SHUTDOWN=1 ;;
        -h|--help) usage; exit 0 ;;
        -*) echo "Unknown option: $arg"; usage; exit 1 ;;
        *) CONFIG="$arg" ;;
    esac
done

if [ $SHUTDOWN -eq 1 ] && [ "$(id -u)" -ne 0 ]; then
    echo "Error: --shutdown requires root. Exiting without running."
    exit 1
fi

if [ -z "$CONFIG" ]
  then
    echo "Sourcing config.rc"
    source config.rc
  else
    echo "Sourcing $CONFIG"
    source $CONFIG
fi

source ./env/bin/activate
python manage.py update_zone `echo $ENABLED_ZONES`
python manage.py run_searches
python manage.py run_alerts
python manage.py purge_new
find ./tmp/*.txt  -mtime +15 -type f  -exec rm {} \;

if [ $SHUTDOWN -eq 1 ]; then
    echo "Run complete. Shutting down."
    shutdown -h now
fi
