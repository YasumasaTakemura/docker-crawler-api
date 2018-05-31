#!/usr/bin/env bash
set -e

flag=$1
type=encrypt
plaintext="./env/.env"
ciphertext="./env/.env.enc"

# decrypt
if [ "${flag}" = "d" ];then
    type=decrypt && \
    touch env/.env
fi

echo $type

gcloud kms $type \
    --location=global \
    --keyring=my-key-ring \
    --key=my-key \
    --ciphertext-file=$ciphertext \
    --plaintext-file=$plaintext