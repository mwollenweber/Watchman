#!/bin/sh

if [ "$#" -ne 1 ]; then
    echo "USAGE: zone2sortedlist <zonefile_name>"
    exit 2
fi

cut -f1 $1 | sort

