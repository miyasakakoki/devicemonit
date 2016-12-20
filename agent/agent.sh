#!/bin/bash

seq=1
while sleep 3; do
	if curl $1; then
		break;
	fi
done
while sleep 60; do
	curl $1 -X POST -d "{\"seq\":${seq}}"
done

