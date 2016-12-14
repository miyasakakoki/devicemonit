#!/bin/bash

WORKER=4
APPNAME="test:app"
BIND="0.0.0.0:445"

gunicorn -b ${BIND} -w ${WORKER} ${APPNAME}
