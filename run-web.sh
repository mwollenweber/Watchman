#!/bin/bash
# Runs the Django web service under gunicorn with production settings.
# Used by watchman-web.service (see install-web.sh); can also be run by hand.
#
# Usage: ./run-web.sh [config-file]
#
# Settings read from the config file:
#   WEB_BIND     address:port gunicorn listens on (default 0.0.0.0:8000)
#   WEB_WORKERS  gunicorn worker processes (default 3)
#   DEBUG        forced off unless the config sets it explicitly

cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1

if [ $# -eq 0 ]
  then
    echo "Sourcing config.rc"
    source config.rc
  else
    echo "Sourcing $1"
    source "$1"
fi

# Production: no debug pages, no debug toolbar, static files from whitenoise
export DEBUG="${DEBUG:-false}"

source ./env/bin/activate
exec gunicorn Watchman.wsgi:application \
    --bind "${WEB_BIND:-0.0.0.0:8000}" \
    --workers "${WEB_WORKERS:-3}" \
    --access-logfile - \
    --error-logfile -
