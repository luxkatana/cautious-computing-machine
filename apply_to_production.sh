#!/usr/bin/sh
git pull

systemctl --user daemon-reload

systemctl --user restart event
