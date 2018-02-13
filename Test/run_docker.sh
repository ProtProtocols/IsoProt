#!/bin/bash

sudo docker run -i -t -v `pwd`:/data/ -e DISPLAY -v $HOME/.Xauthority:/home/developer/.Xauthority --net=host label_pipeline
