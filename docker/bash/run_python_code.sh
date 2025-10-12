#!/bin/bash
set -e

start_time=$(date +%s%N)

timeout 10 /usr/bin/time -f "MEM:%M" -o /code/metrics.txt python3 /code/main.py < /code/input.txt > /code/output.txt 2> /code/error.txt
exit_code=$?

end_time=$(date +%s%N)
elapsed_time=$(( (end_time-start_time) / 1000000))

echo "TIME:$elapsed_time" >> /code/metrics.txt

if [ $exit_code -eq 124 ]; then
    echo "TIMEOUT" > /code/status.txt
    exit 124
elif [ $exit_code -ne 0 ]; then
    echo "RUNTIME_ERROR" > /code/status.txt
    cat /code/error.txt
    exit $exit_code
fi

echo "SUCCESS" > /code/status.txt
cat /code/output.txt
