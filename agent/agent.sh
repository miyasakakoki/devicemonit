#!/bin/bash

seq=1
while sleep 3; do
	curl $1;
	if $?; then break; fi
done
while sleep 60; do
	curl $1 -X POST "\{\"seq\":${seq}\}"
done

