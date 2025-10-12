# Why does my C Docker runner script not detect runtime errors? Exit code is always 0 and error.txt is empty

I am learning to replicate an online judge system (like LeetCode or Codeforces) using Docker to run C code submissions in a sandbox environment. My bash script (running inside the container) is supposed to detect compilation errors, runtime errors, and timeouts. 

However, I'm facing a problem: when the C code causes a runtime error (like division by zero or segmentation fault), the exit code is always 0, the error.txt file is empty, and the status.txt file shows "SUCCESS" instead of "RUNTIME_ERROR".

## My Setup

**Dockerfile (c_runner.dockerfile):**
```dockerfile
FROM gcc:13.2.0

RUN apt-get update && apt-get install -y time bc && rm -rf /var/lib/apt/lists/*

RUN useradd -m runner
RUN mkdir /code && chown -R runner:runner /code

WORKDIR /code

COPY bash/run_c_code.sh /run_c_code.sh
RUN chmod +x /run_c_code.sh

USER runner

ENTRYPOINT [ "/run_c_code.sh" ]
```

**Bash script (run_c_code.sh):**
```bash
#!/bin/bash
set -e

gcc /code/main.c -o /code/a.out 2> /code/compile_error.txt
compile_exit=$?

if [ $compile_exit -ne 0 ]; then
    echo "COMPILE_ERROR"  >> /code/status.txt
    exit $compile_exit
fi

# If compiled, and compile_error.txt exists, it's just a warning
if [ -f /code/compile_error.txt ]; then
    echo "COMPILE_WARNING" >> /code/status.txt
fi

# Run
set +ex

start_time=$(date +%s%N)
timeout 10 /usr/bin/time -f "MEM:%M" -o /code/metrics.txt /code/a.out < /code/input.txt > /code/output.txt 2> /code/error.txt
exit_code=$?
echo "E_CODE=$exit_code" >> /code/status.txt

end_time=$(date +%s%N)
elapsed_time=$(( (end_time-start_time) / 1000000))

echo "TIME:$elapsed_time" >> /code/metrics.txt

if [ $exit_code -eq 124 ]; then
    echo "TIMEOUT" >> /code/status.txt
    exit 124
elif [ $exit_code -ne 0 ]; then
    echo "RUNTIME_ERROR"  >> /code/status.txt
    exit $exit_code
else
    echo "SUCCESS"  >> /code/status.txt
fi
echo "E_CODE=$exit_code" >> /code/status.txt
```

**Python code to execute:**
```python
import subprocess
import tempfile
import os

temp_dir = tempfile.mkdtemp()

# Write test code with division by zero
with open(os.path.join(temp_dir, 'main.c'), 'w') as f:
    f.write("""
#include <stdio.h>
int main() {
    int a = 10;
    int b = 0;
    int c = a / b;  // Division by zero - should cause runtime error
    printf("%d\\n", c);
    return 0;
}
""")

# Create empty input.txt
with open(os.path.join(temp_dir, 'input.txt'), 'w') as f:
    f.write("")

# Run docker
command = ['docker', 'run', '--rm', '-v', f'{temp_dir}:/code', 'seka-c-runner']
result = subprocess.run(command, capture_output=True, text=True, timeout=15)

print(f"Docker return code: {result.returncode}")  # Always shows 0
print(f"Docker stdout: {result.stdout}")
print(f"Docker stderr: {result.stderr}")

# Check files
with open(os.path.join(temp_dir, 'status.txt')) as f:
    print(f"Status: {f.read()}")  # Shows "SUCCESS" instead of "RUNTIME_ERROR"

with open(os.path.join(temp_dir, 'error.txt')) as f:
    print(f"Error output: {f.read()}")  # Always empty!
```

## The Problem

When I run code with runtime errors (division by zero, segmentation fault, array out of bounds), I expect:
- `exit_code` to be non-zero (like 136 for SIGFPE, 139 for SIGSEGV)
- `error.txt` to contain error information
- `status.txt` to contain "RUNTIME_ERROR"

But what actually happens:
- `exit_code` is always 0
- `error.txt` is always empty
- `status.txt` shows "SUCCESS"
- Docker's `result.returncode` from Python is also 0

Even for timeout cases, it doesn't write "TIMEOUT" to status.txt.

**What am I doing wrong?** How can I reliably detect runtime errors in C code when running in this Docker setup? Is there something wrong with how I'm using `timeout`, `/usr/bin/time`, or signal handling?

Any guidance would be greatly appreciated as I'm learning how online judge systems work!