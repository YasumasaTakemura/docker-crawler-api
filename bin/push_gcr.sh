#!/usr/bin/env bash

mode=$#
SOURCE_IMAGE=gcloudsdk
PROJECT_ID=yasu-xxx-training-sandbox

usage_exit() {
        echo "Usage: $0 [-a] [-d dir] item ..." 1>&2
        exit 1
}



while getopts p:s: OPT
do
    case $OPT in
        p)  PROJECT_ID=$OPTARG
            ;;
        s)  SOURCE_IMAGE=$OPTARG
            ;;
        h)  usage_exit
            ;;
        \?) usage_exit
            ;;
    esac
done

docker tag $SOURCE_IMAGE gcr.io/$PROJECT_ID/$SOURCE_IMAGE && \
gcloud docker -- push gcr.io/$PROJECT_ID/$SOURCE_IMAGE