#!/usr/bin/sh
git pull

echo "Stopping unit"
systemctl --user kill -s SIGKILL event
echo "Starting unit"
systemctl --user start event
echo "Successfully Started!"
