#!/usr/bin/sh

systemctl --user daemon-reload
python3 notify_update.py

systemctl --user restart event
