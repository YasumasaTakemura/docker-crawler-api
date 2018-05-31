#!/usr/bin/env bash
set -e

flag=$1
type=encrypt
plaintext=env/.env
ciphertext=env/.env.enc

# decrypt
if [ "${flag}" = "d" ];then
    type=decrypt && \
    touch env/.env
fi

gcloud kms $type \
    --location=global \
    --keyring=my-key-ring \
    --key=my-key \
    --ciphertext-file=env/.env.enc \
    --plaintext-file=env/.env