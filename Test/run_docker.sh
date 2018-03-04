#!/bin/bash

if [ -d "./LocalTest" ]; then
    sudo docker run -it -p 8888:8888 -v `pwd`:/data/ -v `pwd`/LocalTest:/home/biodocker/IN/ veitveit/isolabeledprotocol:latest
else
    sudo docker run -it -p 8888:8888 -v `pwd`:/data/ veitveit/isolabeledprotocol:latest
fi
