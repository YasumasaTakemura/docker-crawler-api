#!/usr/bin/env bash

set -e

SOURCE_IMAGE=$1
PROJECT_ID=yasu-xxx-training-sandbox

usage_exit() {
        if [ -z $SOURCE_IMAGE ];then
            echo "Usage: $0 -s SOURCE_IMAGE [-p PROJECT_ID ] ..." 1>&2
            exit 1
        fi


}


while getopts p:s:h OPT
do
    case $OPT in
        p)  PROJECT_ID=$OPTARG
            ;;
        s)  SOURCE_IMAGE=$OPTARG
            usage_exit
            ;;
        h)  usage_exit
            ;;
        \?) usage_exit
            ;;
    esac
done

docker build -t $SOURCE_IMAGE .
docker tag $SOURCE_IMAGE gcr.io/$PROJECT_ID/$SOURCE_IMAGE
gcloud docker -- push gcr.io/$PROJECT_ID/$SOURCE_IMAGE