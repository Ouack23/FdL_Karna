#!/bin/bash

while [ ! -e /tmp/reboot ]; do
	sleep 1
done

echo "reboot or power of .. " > /tmp/reboot.log

if [ "$(cat /tmp/reboot)" == "REBOOT" ]; then
    echo "REBOOT"
    reboot
else
    echo "POWEROFF"
    poweroff
fi

exit 0
