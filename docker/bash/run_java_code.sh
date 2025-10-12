#!/bin/bash
set -e
# start_time=$(date +%s%N)

#compile java
java_file=$(find /code -name "*.java" | head -n 1)
class_name=$(basename "$java_file" .java)
javac "$java_file" 2> /code/compile_error.txt
compile_exit=$?
if [ $compile_exit -ne 0 ]; then
    echo "COMPILE_ERROR"  > /code/status.txt
    cat /code/compile_error.txt
    exit $compile_exit
fi

# Jika dicompile, dan hasilnya ada, berarti cuman warning
if [ -f /code/compile_error.txt ]; then
        echo "COMPILE_WARNING" > /code/status.txt 
fi

# run
start_time=$(date +%s%N)
timeout 10 /usr/bin/time -f "MEM:%M" -o /code/metrics.txt java "$class_name" < /code/input.txt > /code/output.txt 2> /code/error.txt
exit_code=$?

end_time=$(date +%s%N)
elapsed_time=$(( (end_time-start_time) / 1000000))

echo "TIME:$elapsed_time" >> /code/metrics.txt

if [ $exit_code -eq 124 ]; then
    echo "TIMEOUT"  > /code/status.txt
    exit 124
elif [ $exit_code -ne 0 ]; then
    echo "RUNTIME_ERROR"  > /code/status.txt
    cat /code/error.txt
    exit $exit_code
fi

# success
echo "SUCCESS"  > /code/status.txt
cat /code/output.txt