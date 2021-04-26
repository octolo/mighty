#!/usr/bin/env bash
set -e
source $1/bin/activate
set -o allexport
source $3
$2/manage.py handleStatusMail
deactivate