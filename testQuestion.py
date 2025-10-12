import subprocess
import tempfile
import os

temp_dir = tempfile.mkdtemp()

# Write test code with division by zero
with open(os.path.join(temp_dir, 'main.c'), 'w') as f:
    f.write("""
#include <stdio.h>
int main() {
    int a, b;
    
    scanf("%d %d", &a, &b);
    
    int c = a / b;
    printf("%d\\n", c);
    return 0;
}
""")

# Create empty input.txt
with open(os.path.join(temp_dir, 'input.txt'), 'w') as f:
    f.write("5 2")
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