I am learning to replicate an online judge system. I have a bash script that should detect runtime errors in C code, but the `exit_code` is always 0 even when the program crashes.

**My bash script:**
```bash
#!/bin/bash
set -e

gcc /code/main.c -o /code/a.out 2> /code/compile_error.txt
compile_exit=$?

if [ $compile_exit -ne 0 ]; then
    echo "COMPILE_ERROR" > /code/status.txt
    exit $compile_exit
fi

# Run the program
start_time=$(date +%s%N)
timeout 10 /usr/bin/time -f "MEM:%M" -o /code/metrics.txt /code/a.out < /code/input.txt > /code/output.txt 2> /code/error.txt
exit_code=$?

end_time=$(date +%s%N)
elapsed_time=$(( (end_time-start_time) / 1000000))
echo "TIME:$elapsed_time" >> /code/metrics.txt

if [ $exit_code -eq 124 ]; then
    echo "TIMEOUT" > /code/status.txt
    exit 124
elif [ $exit_code -ne 0 ]; then
    echo "RUNTIME_ERROR" > /code/status.txt
    exit $exit_code
else
    echo "SUCCESS" > /code/status.txt
fi
```

**Test case - main.c with division by zero:**
```c
#include <stdio.h>
int main() {
    int a = 10;
    int b = 0;
    int c = a / b;  // Should cause SIGFPE
    printf("%d\n", c);
    return 0;
}
```

**To reproduce:**
```bash
mkdir test_dir
cd test_dir
# Create main.c with the code above
echo "" > input.txt
bash run_script.sh
echo "Exit code: $?"
cat status.txt
```

## The Problem

I expect:
- `exit_code` to be non-zero (136 for SIGFPE or 139 for SIGSEGV)
- `status.txt` to contain "RUNTIME_ERROR"

But what happens:
- `exit_code` is always **0**
- `status.txt` shows "SUCCESS"
- `error.txt` is empty

The same issue occurs with segmentation faults. Why is the exit code not capturing the signal/crash, and how can I reliably detect runtime errors?