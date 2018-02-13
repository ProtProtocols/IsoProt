#!/bin/bash
sudo docker container prune -f
sudo docker rmi label_pipeline

sudo docker build -t label_pipeline .
