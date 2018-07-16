#!/bin/bash


img_name="veitveit/isolabeledprotocol" 
if [ -n "$1" ]; then img_name=$1; fi

# TODO  have an option to override with named parameter
# (my bash skills are not good enough) 
data=`pwd`

# Make sure docker is installed
DOCKER_CMD=`command -v docker`

if [ -z "${DOCKER_CMD}" ]; then
    echo "Error: Canot find 'docker' command."
    echo -e "To install Docker on your system please visit\nhttps://www.docker.com/community-edition"
    exit 1
fi

# test if root access is needed
IN_DOCKER_GROUP=`id | grep -c "docker"`

if [ $IN_DOCKER_GROUP == 1 ]; then
    DOCKER_CMD="docker"
else
    # get root access
    echo "Launching docker requires root access..."
    sudo echo ""

    if [ $? != 0 ]; then
        echo "Error: Failed to get root access."
        exit 1
    fi

    DOCKER_CMD="sudo docker"
fi

# Make sure the image is installed
IMG_COUNT=`${DOCKER_CMD} image ls | grep -c "${img_name}"`

if [ ${IMG_COUNT} -lt 1 ]; then
    echo "Docker image '${img_name}' is not installed."
    echo -n "Do you want to install it [y/n]: "
    read INSTALL_IMG
    
    if [ "${INSTALL_IMG}" != "y" ]; then
        exit 1
    fi

    # install the image
    ${DOCKER_CMD} pull ${img_name}

    if [ $? != 0 ]; then
        echo "Error: Failed to install docker image."
        exit 1
    fi
fi

# find  first free port 
# There is probably a better way
PORT=`python -c "
import socket, itertools
from socket import error as socket_error
s = socket.socket()
for port in itertools.count(8888):
    try: s.bind(('', port)); break
    except Exception: continue
print(port)
"` 

# make sure the PORT was found
if [ -z "${PORT}" ]; then
    echo "Error: Failed to find free port."
    exit 1
fi

# create the OUT directory
if [ ! -d "OUT" ]; then
    mkdir OUT

    if [ $? != 0 ]; then
        echo "Error: Failed to create result directory ('OUT')."
        exit 1
    fi
fi

# OK, let's hope there are no race conditions as this isn't really atomic

ADRESS="http://localhost:$PORT/" 
echo "using port:" $PORT
echo $ADRESS

# Launch the webbrowser with a 10 second delay
( sleep 3 ; xdg-open $ADRESS) &

# Launch the docker image
${DOCKER_CMD} run -it -p $PORT:${PORT} -v $data:/data/ -v ${data}/OUT:/home/biodocker/OUT $img_name jupyter notebook --ip=0.0.0.0 --port=${PORT} --no-browser
