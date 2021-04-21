#!/usr/bin/env bash
set -e
source $1/bin/activate
/home/gyn/Projects/Octolo/Octolo/manage.py handleStatusMail
deactivate