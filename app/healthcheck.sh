#!/bin/sh

exit $(( (`date +%s` - `stat -L -c %Y /log/ksem-mqtt-status.log` ) > 60 ))
