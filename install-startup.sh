#!/bin/bash
# Installs a systemd service that runs run-daily.sh once every time the system boots.

SERVICE_NAME="watchman-daily"
UNIT_FILE="/etc/systemd/system/$SERVICE_NAME.service"
SUDOERS_FILE="/etc/sudoers.d/$SERVICE_NAME-shutdown"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
    echo "Usage: sudo $0 [--shutdown] [--config FILE] [--user USER] [--dry-run]"
    echo "       sudo $0 --uninstall"
    echo "  --shutdown     Pass --shutdown to run-daily.sh so the system powers off after the run,"
    echo "                 and allow USER to run shutdown through sudo without a password"
    echo "  --config FILE  Config file for run-daily.sh (default: config.rc)"
    echo "  --user USER    User the run happens as (default: the user who ran sudo)"
    echo "  --dry-run      Print what would be installed without changing anything"
    echo "  --uninstall    Disable and remove the service and sudoers rule"
}

SHUTDOWN=0
CONFIG=""
RUN_USER="${SUDO_USER:-$(id -un)}"
DRY_RUN=0
UNINSTALL=0
while [ $# -gt 0 ]; do
    case "$1" in
        --shutdown) SHUTDOWN=1 ;;
        --config) CONFIG="$2"; shift ;;
        --user) RUN_USER="$2"; shift ;;
        --dry-run) DRY_RUN=1 ;;
        --uninstall) UNINSTALL=1 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
    shift
done

if [ $DRY_RUN -eq 0 ]; then
    if ! command -v systemctl >/dev/null 2>&1; then
        echo "Error: systemd is required (systemctl not found)."
        exit 1
    fi
    if [ "$(id -u)" -ne 0 ]; then
        echo "Error: run this with sudo; it writes to /etc/systemd/system."
        exit 1
    fi
fi

if [ $UNINSTALL -eq 1 ]; then
    systemctl disable "$SERVICE_NAME.service" 2>/dev/null
    rm -f "$UNIT_FILE" "$SUDOERS_FILE"
    systemctl daemon-reload
    echo "Removed $SERVICE_NAME.service"
    exit 0
fi

if [ "$RUN_USER" = "root" ]; then
    echo "Error: refusing to run Watchman as root. Use --user, or run this script with sudo from your normal account."
    exit 1
fi
if ! id "$RUN_USER" >/dev/null 2>&1; then
    echo "Error: user $RUN_USER doesn't exist."
    exit 1
fi

if [ -n "$CONFIG" ]; then
    # run-daily.sh sources the config relative to APP_DIR
    case "$CONFIG" in
        /*) ;;
        *) CONFIG="$APP_DIR/$CONFIG" ;;
    esac
fi
if [ ! -f "${CONFIG:-$APP_DIR/config.rc}" ]; then
    echo "Error: config file ${CONFIG:-$APP_DIR/config.rc} not found."
    exit 1
fi

# Unit files split ExecStart on spaces, so quote each argument
exec_args="\"$APP_DIR/run-daily.sh\""
[ -n "$CONFIG" ] && exec_args="$exec_args \"$CONFIG\""
[ $SHUTDOWN -eq 1 ] && exec_args="$exec_args --shutdown"

unit="[Unit]
Description=Watchman daily zone update, searches and alerts
Wants=network-online.target
After=network-online.target postgresql.service redis.service redis6.service

[Service]
Type=oneshot
User=$RUN_USER
WorkingDirectory=$APP_DIR
ExecStart=/bin/bash $exec_args
# Zone updates can take hours
TimeoutStartSec=infinity

[Install]
WantedBy=multi-user.target"

shutdown_bin=$(command -v shutdown || echo /sbin/shutdown)
sudoers_rule="$RUN_USER ALL=(root) NOPASSWD: $shutdown_bin -h now"

if [ $DRY_RUN -eq 1 ]; then
    echo "# $UNIT_FILE"
    echo "$unit"
    if [ $SHUTDOWN -eq 1 ]; then
        echo
        echo "# $SUDOERS_FILE"
        echo "$sudoers_rule"
    fi
    exit 0
fi

if [ $SHUTDOWN -eq 1 ]; then
    tmp=$(mktemp)
    echo "$sudoers_rule" > "$tmp"
    if ! visudo -c -q -f "$tmp"; then
        rm -f "$tmp"
        echo "Error: generated sudoers rule failed validation; nothing was installed."
        exit 1
    fi
    install -m 0440 -o root -g root "$tmp" "$SUDOERS_FILE"
    rm -f "$tmp"
    echo "Allowed $RUN_USER to run '$shutdown_bin -h now' without a password ($SUDOERS_FILE)"
else
    rm -f "$SUDOERS_FILE"
fi

echo "$unit" > "$UNIT_FILE"
chmod 0644 "$UNIT_FILE"
systemctl daemon-reload
systemctl enable "$SERVICE_NAME.service"

echo "Installed $SERVICE_NAME.service. run-daily.sh will run as $RUN_USER on every boot."
[ $SHUTDOWN -eq 1 ] && echo "The system will power off after each run. To skip that during maintenance: sudo systemctl stop $SERVICE_NAME"
echo "Run it now:   sudo systemctl start $SERVICE_NAME"
echo "Follow logs:  journalctl -u $SERVICE_NAME -f"
echo "Remove it:    sudo $0 --uninstall"
