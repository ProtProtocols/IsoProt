#!/bin/bash

# Make sure the container is running
CONTAINER_NAME="veitveit/isolabeledprotocol:latest"

CONTAINER_RUNNING=`sudo docker container ls | grep -c "${CONTAINER_NAME}"`

if [ "$CONTAINER_RUNNING" != "1" ]; then
    echo "Error: Jobskee container is not running"
    exit 1
fi

# Get the container id
CONTAINER_ID=`sudo docker container ls | grep "${CONTAINER_NAME}" | sed 's|\([0-9a-z]*\).*|\1|'`

# Launch bash
sudo docker exec -t -i $CONTAINER_ID bash
