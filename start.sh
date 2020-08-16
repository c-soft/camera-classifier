#!/usr/bin/env bashio

RTSP_URL="$(bashio::config 'rtsp_url')"
export RTSP_URL

python3 app.py
