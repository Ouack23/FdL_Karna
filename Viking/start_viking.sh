#!/bin/bash
# Start viking

while [ -e /tmp/viking.lock ]; do
    sleep 1     # unable to run vicking when lock (for test)
done

while [ ! "$(ps -ejH | grep olad)" ]; do
    sleep 1
done
sleep 3     # ensure olad is really started

while [ ! "$(ps -ejH | grep pigpiod)" ]; do
    sleep 1
done
sleep 1     # ensure pigpiod is really started

/usr/bin/python2.7 viking.py

exit $?