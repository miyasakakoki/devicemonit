#!/bin/bash

seq=0
if cat log 2>/dev/null 1>/dev/null; then
	log=`cat log`
else
	log=0
fi
while true; do
	dat=`echo "{\"seq\":${seq}, \"stat\":\"OK\", \"log\":{\"seq\":${log}}}"`
	echo $dat
	if curl -X POST -d "${dat}" http://${1}/${2} -sS -m 1 -H "Accept: application/json" -H "Content-type: application/json"; then
		seq=0
		rm log 2> /dev/null
	else
		seq=$((++seq))
		if [ ${log} -eq 0 ]; then
			echo ${seq}>log
		fi
	fi
	sleep 30
done



