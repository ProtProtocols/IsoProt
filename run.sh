#!/bin/bash


img_name="veitveit/isoprot" 
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

# find  first free port, starting from 8888
let PORT=8888                                                                   
while ( netstat -an | grep :${PORT} &> /dev/null ); do let PORT++; done 

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

# make sure the directory is writeable
if [ ! -w "OUT" ]; then
    echo "Error: Missing premissions to write into 'OUT' directory."
    exit 1
fi

# OK, let's hope there are no race conditions as this isn't really atomic

ADRESS="http://localhost:$PORT/"
echo "Adress: $ADRESS"

curl_path=`command -v curl`
wget_path=`command -v wget`
http_path=`command -v http`

# Craete is_server_ready function (based on curl and wget availability)
# to check if jupyter notebook is up and running

if [ -n "$http_path" ]; then
  is_server_ready(){
    http GET $ADRESS &> /dev/null 
  }
elif [ -n "$curl_path" ]; then
  is_server_ready(){
    curl --silent -I $ADRESS # -I for http header only
  }
elif [ -n "$wget_path" ]; then
  is_server_ready(){
    wget --quiet -O - $ADRESS &> /dev/null
  }
else
  is_server_ready(){
    echo -e "\033[33mPlease install 'http', 'curl', or 'wget' for better user experience\033[0m"
    sleep 5
  }
fi

# Launch the webbrowser when jupyter notebbok becomes acssesable
(
  (exit 1) # set $? to "1", while will fail
  while [ $? != "0" ]; do is_server_ready; done  # loop until server is ready
  xdg-open $ADRESS 
) &


# Launch the docker image
${DOCKER_CMD} run -it -p $PORT:${PORT} -v $data:/data/ -v ${data}/OUT:/home/biodocker/OUT $img_name jupyter notebook --ip=0.0.0.0 --port=${PORT} --no-browser
