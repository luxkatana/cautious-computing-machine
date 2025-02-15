#!/usr/bin/sh
git pull

echo "Stopping unit (Kill)"
sudo systemctl kill -s SIGKILL event
echo "Starting unit"
sudo systemctl start event
echo "Successfully Started!"
