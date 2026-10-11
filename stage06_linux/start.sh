#!/bin/bash
# Start the SSH server in the foreground so the container keeps running
service ssh start
tail -f /dev/null
