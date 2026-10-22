#!/bin/bash
# Sourced by install.sh and upgrade.sh. Makes sure ./env is a virtualenv
# running a Python new enough for requirements.txt, installing that Python
# with the system package manager if needed.

MIN_PYTHON="3.12"

python_ok() {
    "$1" -c "import sys; sys.exit(sys.version_info < tuple(map(int, '$MIN_PYTHON'.split('.'))))" 2>/dev/null
}

find_python() {
    local py
    for py in python3.15 python3.14 python3.13 python3.12 python3; do
        if command -v "$py" >/dev/null 2>&1 && python_ok "$(command -v "$py")"; then
            command -v "$py"
            return 0
        fi
    done
    return 1
}

# Installs Python $MIN_PYTHON with the system package manager
install_python() {
    local sudo=""
    [ "$(id -u)" -ne 0 ] && sudo="sudo"

    echo "Installing Python $MIN_PYTHON"
    if command -v dnf >/dev/null 2>&1; then
        $sudo dnf install -y "python$MIN_PYTHON" "python$MIN_PYTHON-pip"
    elif command -v apt-get >/dev/null 2>&1; then
        $sudo apt-get update && $sudo apt-get install -y "python$MIN_PYTHON" "python$MIN_PYTHON-venv"
    elif command -v brew >/dev/null 2>&1; then
        brew install python
    else
        echo "No supported package manager (dnf, apt-get, brew) found."
        return 1
    fi
}

ensure_env() {
    if [ -x env/bin/python ] && python_ok env/bin/python; then
        return 0
    fi

    local py
    if ! py=$(find_python); then
        install_python || true
        hash -r
        if ! py=$(find_python); then
            echo "Error: Python $MIN_PYTHON or newer is required and couldn't be installed."
            return 1
        fi
    fi

    if [ -d env ]; then
        echo "Rebuilding env with $py ($("$py" --version)); it was on $(env/bin/python --version 2>&1)"
    else
        echo "Creating env with $py ($("$py" --version))"
    fi
    "$py" -m venv --clear env
}
