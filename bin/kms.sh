#!/usr/bin/env bash
set -e


flag=$1
type=encrypt
plaintext=$PWD/env/.env
ciphertext=$PWD/env/.env.enc

if [ "$flag" = "d" ];then
    type=decrypt && \
    touch $PWD/env/.env
fi

gcloud kms $type \
    --location=global \
    --keyring=my-key-ring \
    --key=my-key \
    --ciphertext-file=$PWD/env/.env.enc \
    --plaintext-file=$PWD/env/.env