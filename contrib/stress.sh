#! /bin/bash

MAX=500
for count in $(seq 1 $MAX)
do
	R=$[RANDOM%60]
	echo "PUSH [$count] repo:repo${count}$R   cmd: sleep $R    result: "$(echo '{"repo": "repo'${count}$R'", "ref": "tRef", "cmd": "sleep '$R'", "priority": '$[count+RANDOM]'}' | nc localhost 9999)&
done
for job in `jobs -p`
do
	echo "Waiting for job $job"
	wait $job
done
