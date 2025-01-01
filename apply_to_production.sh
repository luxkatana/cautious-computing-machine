#!/usr/bin/sh
git pull

systemctl --user daemon-reload
python3 notify_update.py

systemctl --user restart event
