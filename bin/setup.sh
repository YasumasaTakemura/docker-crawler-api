##!/usr/bin/env bash
#
#
## read params from .env
#if [ ! -f  "./env/.env" ]; then
#    touch ./env/.env
#fi
#
##decrypt env file
#bash ./bin/kms.sh d
## python ./env/settings.py
#
#PROJECT_ID=yasu-xxx-training-sandbox
#
#
#sed -e "s/SQLPROXY_IMG_VERSION/${PROJECT_ID}/g" \
#    ./template/docker-compose-template.yml  >  ./docker-compose.yml
#
#docker-compose up -d && rm ./docker-compose.yml $PWD/env/.env
