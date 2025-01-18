#!/usr/bin/sh
git pull

echo "Restarting unit"
systemctl --user restart event
echo "Successfully restarted!"
