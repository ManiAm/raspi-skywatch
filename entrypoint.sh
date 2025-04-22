#!/bin/bash

# Start lighttpd in foreground
lighttpd -D -f /etc/lighttpd/lighttpd.conf &

mkdir -p /run/dump1090-fa

exec /opt/dump1090/dump1090 \
  --net \
  --net-bo-port 30005 \
  --device-index 0 \
  --write-json /run/dump1090-fa \
  --lat "$LAT" \
  --lon "$LON"
