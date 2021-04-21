#!/usr/bin/env bash
set -e
source $1/bin/activate
$2/manage.py handleStatusMail
deactivate