#! /bin/sh
set -e 
echo "Going to sleep"
sleep 15
echo "Waking up"
exec pytest -v
