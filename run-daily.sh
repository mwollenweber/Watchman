#!/bin/bash

usage() {
    echo "Usage: $0 [--shutdown] [config-file]"
    echo "  --shutdown   Shut down the system when the run finishes (requires permission to shut down)"
}

# Sets SHUTDOWN_CMD to a command this user is allowed to run without a password
# prompt, or returns 1 if the user can't shut down the system.
find_shutdown_cmd() {
    local bin
    bin=$(command -v shutdown || echo /sbin/shutdown)

    if [ "$(id -u)" -eq 0 ]; then
        SHUTDOWN_CMD=("$bin" -h now)
        return 0
    fi

    # Passwordless sudo rule for shutdown. -k ignores cached credentials, which
    # may have expired by the time the run finishes.
    if sudo -k -n -l "$bin" -h now >/dev/null 2>&1; then
        SHUTDOWN_CMD=(sudo -n "$bin" -h now)
        return 0
    fi

    # systemd-logind/polkit allows this user to power off without authentication
    if command -v busctl >/dev/null 2>&1 &&
        busctl call org.freedesktop.login1 /org/freedesktop/login1 \
            org.freedesktop.login1.Manager CanPowerOff 2>/dev/null | grep -q '"yes"'; then
        SHUTDOWN_CMD=(systemctl poweroff)
        return 0
    fi

    return 1
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

if [ $SHUTDOWN -eq 1 ] && ! find_shutdown_cmd; then
    echo "Error: --shutdown was given but $(id -un) doesn't have permission to shut down the system."
    echo "Grant it with a passwordless sudoers rule for $(command -v shutdown || echo /sbin/shutdown). Exiting without running."
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
    "${SHUTDOWN_CMD[@]}"
fi
