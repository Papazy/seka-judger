# kode berbahaya
malicious_code_python =  '''
import os
import shutil

# kode untuk delete file
files_to_delete = [
    "test_security/important_data.txt",
    "test_security/user_database.db", 
    "test_security/config.json",
    "test_security/secret_key.pem"

]

print("Starting malicious file deletion...")

for file_path in files_to_delete:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"DELETED: {file_path}")
        else:
            print(f"NOT FOUND: {file_path}")
    except Exception as e:
        print(f"ERROR deleting {file_path}: {e}")

# Try to delete entire directory
try:
    if os.path.exists("test_security"):
        shutil.rmtree("test_security")
        print("DELETED ENTIRE DIRECTORY: test_security/")
except Exception as e:
    print(f"ERROR deleting directory: {e}")

# Print something normal to hide the attack
a, b = map(int, input().split())
print(a + b)
'''

# system gathering
system_info_code = '''
import os
import subprocess
import socket

print("=== SYSTEM INFORMATION GATHERED ===")

# Get current directory and list files
print(f"Current Directory: {os.getcwd()}")
print("Files in current directory:")
try:
    for item in os.listdir("."):
        print(f"  {item}")
except:
    pass

# Get environment variables
print("\\nEnvironment Variables:")
for key, value in os.environ.items():
    if key in ['PATH', 'USERNAME', 'COMPUTERNAME', 'OS']:
        print(f"  {key}: {value}")

# Get network info
print(f"\\nHostname: {socket.gethostname()}")

# Try to run system commands
try:
    result = subprocess.run(['whoami'], capture_output=True, text=True)
    print(f"Current User: {result.stdout.strip()}")
except:
    pass

# Print normal output to hide attack
a, b = map(int, input().split())
print(a + b)
'''