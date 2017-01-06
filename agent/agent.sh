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
	tmp=`curl -X POST -d "${dat}" http://${1}/${2} -sS -m 1 -H "Accept: application/json" -H "Content-type: application/json"`
	if [ $? eq 0 ]; then
		seq=0
		rm log 2> /dev/null
	else
		seq=$((++seq))
		if [ ${log} -eq 0 ]; then
			echo ${seq}>log
		fi
	fi
	cmd=`echo ${tmp} | sed "s/^.*\"command\" ?: ?\"\(.*\)\".*$/%1/g"`
	if [ $cmd -eq "shutdown" ]; then
		shutdown -h now
	elif [ $cmd -eq "reboot" ]; then
		reboot
	fi
	sleep 60
done



