#!/bin/bash


if [ -f "$1" ]; then
    eval 'set -o allexport'
    eval 'source $1'
    eval 'set +o allexport'
    echo $ENV
else
    echo "ko"
fi