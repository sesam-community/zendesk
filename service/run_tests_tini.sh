#! /bin/sh
set -e 
echo "Going to sleep. Making sure other services have started."
sleep 2
echo "Waking up"
exec pytest -v
