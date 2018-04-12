#!/usr/bin/env bash

set -e

flg=$#
SOURCE_IMAGE=$1
PROJECT_ID=yasu-xxx-training-sandbox

usage_exit() {
        if [  $flg -eq  0 ] || [ -z $SOURCE_IMAGE ];then
            echo "Usage: bash $0 -s <SOURCE_IMAGE> [-p <PROJECT_ID> ] ..." 1>&2
            exit 1
        fi
}

# validation
usage_exit

# check args
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