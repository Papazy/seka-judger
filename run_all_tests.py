#!/usr/bin/env python3
"""
Automated Test Runner untuk Judge API
Menjalankan semua test cases yang ada di test.md
"""

import requests
import json
import time
from typing import Dict, List, Optional
from datetime import datetime

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Base URL
BASE_URL = "http://localhost:8000/v2/judge"

# Test statistics
stats = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "errors": 0,
    "skipped": 0
}

def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_test_name(name: str):
    """Print test name"""
    print(f"{Colors.OKCYAN}{Colors.BOLD}{name}{Colors.ENDC}")

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_failure(message: str):
    """Print failure message"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_info(message: str):
    """Print info message"""
    print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")

def run_test(name: str, payload: Dict, expected_verdict: str, should_skip: bool = False) -> bool:
    """
    Run a single test case
    
    Args:
        name: Test name
        payload: Request payload
        expected_verdict: Expected verdict (AC, WA, TLE, RE, CE, MLE)
        should_skip: Whether to skip this test
    
    Returns:
        True if test passed, False otherwise
    """
    stats["total"] += 1
    print_test_name(f"\n{stats['total']}. {name}")
    
    if should_skip:
        print_warning("SKIPPED - Test may take too long or cause issues")
        stats["skipped"] += 1
        return True
    
    try:
        # Send request
        print_info(f"Sending request to {BASE_URL}...")
        start_time = time.time()
        response = requests.post(BASE_URL, json=payload, timeout=30)
        elapsed_time = time.time() - start_time
        
        # Check if request was successful
        if response.status_code != 200:
            print_failure(f"HTTP Error {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            stats["errors"] += 1
            return False
        
        # Parse response
        result = response.json()
        
        # Check if there's an error in response
        if "error" in result:
            print_failure(f"API Error: {result['error']}")
            stats["errors"] += 1
            return False
        
        # Get verdict
        actual_verdict = result.get("verdict", "UNKNOWN")
        score = result.get("score", 0)
        total_cases = result.get("total_cases", 0)
        passed_cases = result.get("passed_cases", 0)
        max_time_ms = result.get("max_time_ms", 0)
        max_memory_kb = result.get("max_memory_kb", 0)
        
        # Print results
        print_info(f"Elapsed time: {elapsed_time:.2f}s")
        print_info(f"Verdict: {actual_verdict} | Score: {score}/100 | Passed: {passed_cases}/{total_cases}")
        print_info(f"Max Time: {max_time_ms}ms | Max Memory: {max_memory_kb}KB")
        
        # Check if verdict matches expected
        if actual_verdict == expected_verdict:
            print_success(f"PASS - Got expected verdict: {expected_verdict}")
            stats["passed"] += 1
            return True
        else:
            print_failure(f"FAIL - Expected {expected_verdict}, got {actual_verdict}")
            
            # Print detailed test results if available
            if "test_results" in result and result["test_results"]:
                print_info("\nTest case details:")
                for tr in result["test_results"][:3]:  # Show first 3 test cases
                    print(f"  Case {tr['case_number']}: {tr['verdict']} "
                          f"({tr['time_ms']}ms, {tr['memory_kb']}KB)")
                    if tr.get('error_message'):
                        print(f"    Error: {tr['error_message'][:100]}")
            
            stats["failed"] += 1
            return False
            
    except requests.exceptions.Timeout:
        print_failure("TIMEOUT - Request took too long (>30s)")
        stats["errors"] += 1
        return False
    except requests.exceptions.ConnectionError:
        print_failure("CONNECTION ERROR - Cannot connect to server")
        print_warning("Make sure the server is running: uvicorn main:app --reload")
        stats["errors"] += 1
        return False
    except Exception as e:
        print_failure(f"EXCEPTION - {type(e).__name__}: {str(e)}")
        stats["errors"] += 1
        return False

def main():
    """Main test runner"""
    print_header("🚀 Starting Judge API Test Suite")
    print_info(f"Target: {BASE_URL}")
    print_info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    try:
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        if health_response.status_code == 200:
            print_success("Server is running!")
        else:
            print_warning("Server health check returned non-200 status")
    except:
        print_failure("Cannot connect to server!")
        print_warning("Please start the server first: uvicorn main:app --reload")
        return
    
    # ========================================================================
    # PYTHON TESTS
    # ========================================================================
    print_header("1. PYTHON TESTS")
    
    # Test 1.1: Python - All Accepted
    run_test(
        "Python - All Accepted (AC)",
        {
            "code": "a, b = map(int, input().split())\nprint(a + b)",
            "language": "python",
            "test_cases": [
                {"input": "2 2", "expected_output": "4"},
                {"input": "5 5", "expected_output": "10"},
                {"input": "3 3", "expected_output": "6"}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "AC"
    )
    
    # Test 1.2: Python - Wrong Answer
    run_test(
        "Python - Wrong Answer (WA)",
        {
            "code": "a, b = map(int, input().split())\nprint(a * b)",
            "language": "python",
            "test_cases": [
                {"input": "2 2", "expected_output": "4"},
                {"input": "5 5", "expected_output": "10"},
                {"input": "3 3", "expected_output": "6"}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "WA"
    )
    
    # Test 1.3: Python - Time Limit Exceeded (SKIP - takes too long)
    run_test(
        "Python - Time Limit Exceeded (TLE)",
        {
            "code": "while True:\n    pass",
            "language": "python",
            "test_cases": [
                {"input": "", "expected_output": ""}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "TLE",
        should_skip=True  # Skip TLE tests to save time
    )
    
    # Test 1.4: Python - Runtime Error (Division by Zero)
    run_test(
        "Python - Runtime Error - Division by Zero",
        {
            "code": "print(1 / 0)",
            "language": "python",
            "test_cases": [
                {"input": "", "expected_output": ""}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "RTE"
    )
    
    # Test 1.5: Python - Runtime Error (Index Out of Range)
    run_test(
        "Python - Runtime Error - Index Out of Range",
        {
            "code": "arr = [1, 2, 3]\nprint(arr[10])",
            "language": "python",
            "test_cases": [
                {"input": "", "expected_output": ""}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "RTE"
    )
    
    # Test 1.6: Python - Syntax Error
    run_test(
        "Python - Syntax Error (becomes RE)",
        {
            "code": "print('Hello World'",
            "language": "python",
            "test_cases": [
                {"input": "", "expected_output": "Hello World"}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "RTE"
    )
    
    # Test 1.7: Python - Partial Accepted
    run_test(
        "Python - Partial Accepted",
        {
            "code": "a, b = map(int, input().split())\nif a == 2:\n    print(a + b)\nelse:\n    print(a * b)",
            "language": "python",
            "test_cases": [
                {"input": "2 2", "expected_output": "4"},
                {"input": "5 5", "expected_output": "10"},
                {"input": "3 3", "expected_output": "6"}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "WA"  # Because only 1 out of 3 passes
    )
    
    # ========================================================================
    # C TESTS
    # ========================================================================
    print_header("2. C TESTS")
    
    # Test 2.1: C - All Accepted
    run_test(
        "C - All Accepted (AC)",
        {
            "code": "#include <stdio.h>\nint main() {\n    int a, b;\n    scanf(\"%d %d\", &a, &b);\n    printf(\"%d\\n\", a + b);\n    return 0;\n}",
            "language": "c",
            "test_cases": [
                {"input": "2 2", "expected_output": "4"},
                {"input": "5 5", "expected_output": "10"},
                {"input": "3 3", "expected_output": "6"}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "AC"
    )
    
    # Test 2.2: C - Wrong Answer
    run_test(
        "C - Wrong Answer (WA)",
        {
            "code": "#include <stdio.h>\nint main() {\n    int a, b;\n    scanf(\"%d %d\", &a, &b);\n    printf(\"%d\\n\", a * b);\n    return 0;\n}",
            "language": "c",
            "test_cases": [
                {"input": "2 2", "expected_output": "4"},
                {"input": "5 5", "expected_output": "10"},
                {"input": "3 3", "expected_output": "6"}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "WA"
    )
    
    # Test 2.3: C - TLE (SKIP)
    run_test(
        "C - Time Limit Exceeded (TLE)",
        {
            "code": "#include <stdio.h>\nint main() {\n    while(1) {}\n    return 0;\n}",
            "language": "c",
            "test_cases": [
                {"input": "", "expected_output": ""}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "TLE",
        should_skip=True
    )
    
    # Test 2.4: C - Runtime Error (Division by Zero)
    run_test(
        "C - Runtime Error - Division by Zero",
        {
            "code": "#include <stdio.h>\nint main() {\n    int x = 5 / 0;\n    printf(\"%d\\n\", x);\n    return 0;\n}",
            "language": "c",
            "test_cases": [
                {"input": "", "expected_output": ""}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "RTE"
    )
    
    # Test 2.5: C - Runtime Error (Segmentation Fault)
    run_test(
        "C - Runtime Error - Segmentation Fault",
        {
            "code": "#include <stdio.h>\nint main() {\n    int *ptr = NULL;\n    printf(\"%d\\n\", *ptr);\n    return 0;\n}",
            "language": "c",
            "test_cases": [
                {"input": "", "expected_output": ""}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "RTE"
    )
    
    # Test 2.6: C - Compilation Error
    run_test(
        "C - Compilation Error (CE)",
        {
            "code": "#include <stdio.h>\nint main() {\n    printf(\"Hello World\"\n    return 0;\n}",
            "language": "c",
            "test_cases": [
                {"input": "", "expected_output": "Hello World"}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "CE"
    )
    
    # Test 2.7: C - Compilation Error (Undefined Function)
    run_test(
        "C - Compilation Error - Undefined Function",
        {
            "code": "#include <stdio.h>\nint main() {\n    undefinedFunction();\n    return 0;\n}",
            "language": "c",
            "test_cases": [
                {"input": "", "expected_output": ""}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "CE"
    )
    
    # ========================================================================
    # C++ TESTS
    # ========================================================================
    print_header("3. C++ TESTS")
    
    # Test 3.1: C++ - All Accepted
    run_test(
        "C++ - All Accepted (AC)",
        {
            "code": "#include <iostream>\nusing namespace std;\nint main() {\n    int a, b;\n    cin >> a >> b;\n    cout << a + b << endl;\n    return 0;\n}",
            "language": "cpp",
            "test_cases": [
                {"input": "2 2", "expected_output": "4"},
                {"input": "5 5", "expected_output": "10"},
                {"input": "3 3", "expected_output": "6"}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "AC"
    )
    
    # Test 3.2: C++ - Wrong Answer
    run_test(
        "C++ - Wrong Answer (WA)",
        {
            "code": "#include <iostream>\nusing namespace std;\nint main() {\n    int a, b;\n    cin >> a >> b;\n    cout << a - b << endl;\n    return 0;\n}",
            "language": "cpp",
            "test_cases": [
                {"input": "5 3", "expected_output": "8"},
                {"input": "10 5", "expected_output": "15"}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "WA"
    )
    
    # Test 3.3: C++ - TLE (SKIP)
    run_test(
        "C++ - Time Limit Exceeded (TLE)",
        {
            "code": "#include <iostream>\nusing namespace std;\nint main() {\n    while(true) {}\n    return 0;\n}",
            "language": "cpp",
            "test_cases": [
                {"input": "", "expected_output": ""}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "TLE",
        should_skip=True
    )
    
    # Test 3.4: C++ - Runtime Error (Exception)
    run_test(
        "C++ - Runtime Error - Exception",
        {
            "code": "#include <iostream>\n#include <stdexcept>\nusing namespace std;\nint main() {\n    throw runtime_error(\"Error!\");\n    return 0;\n}",
            "language": "cpp",
            "test_cases": [
                {"input": "", "expected_output": ""}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "RTE"
    )
    
    # Test 3.5: C++ - Compilation Error
    run_test(
        "C++ - Compilation Error (CE)",
        {
            "code": "#include <iostream>\nusing namespace std;\nint main() {\n    cout << \"Hello\" << end;\n    return 0;\n}",
            "language": "cpp",
            "test_cases": [
                {"input": "", "expected_output": "Hello"}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "CE"
    )
    
    # Test 3.6: C++ - Compilation Error (Missing Semicolon)
    run_test(
        "C++ - Compilation Error - Missing Semicolon",
        {
            "code": "#include <iostream>\nusing namespace std;\nint main() {\n    int x = 5\n    cout << x << endl;\n    return 0;\n}",
            "language": "cpp",
            "test_cases": [
                {"input": "", "expected_output": "5"}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "CE"
    )
    
    # ========================================================================
    # JAVA TESTS
    # ========================================================================
    print_header("4. JAVA TESTS")
    
    # Test 4.1: Java - All Accepted
    run_test(
        "Java - All Accepted (AC)",
        {
            "code": "import java.util.Scanner;\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int a = sc.nextInt();\n        int b = sc.nextInt();\n        System.out.println(a + b);\n        sc.close();\n    }\n}",
            "language": "java",
            "test_cases": [
                {"input": "2 2", "expected_output": "4"},
                {"input": "5 5", "expected_output": "10"},
                {"input": "3 3", "expected_output": "6"}
            ],
            "time_limit_ms": 2000,
            "memory_limit_kb": 262144
        },
        "AC"
    )
    
    # Test 4.2: Java - Wrong Answer
    run_test(
        "Java - Wrong Answer (WA)",
        {
            "code": "import java.util.Scanner;\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int a = sc.nextInt();\n        int b = sc.nextInt();\n        System.out.println(a * b);\n        sc.close();\n    }\n}",
            "language": "java",
            "test_cases": [
                {"input": "2 2", "expected_output": "4"},
                {"input": "5 5", "expected_output": "10"},
                {"input": "3 3", "expected_output": "6"}
            ],
            "time_limit_ms": 2000,
            "memory_limit_kb": 262144
        },
        "WA"
    )
    
    # Test 4.3: Java - TLE (SKIP)
    run_test(
        "Java - Time Limit Exceeded (TLE)",
        {
            "code": "public class Main {\n    public static void main(String[] args) {\n        while(true) {}\n    }\n}",
            "language": "java",
            "test_cases": [
                {"input": "", "expected_output": ""}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "TLE",
        should_skip=True
    )
    
    # Test 4.4: Java - Runtime Error (Division by Zero)
    run_test(
        "Java - Runtime Error - Division by Zero",
        {
            "code": "public class Main {\n    public static void main(String[] args) {\n        int x = 5 / 0;\n        System.out.println(x);\n    }\n}",
            "language": "java",
            "test_cases": [
                {"input": "", "expected_output": ""}
            ],
            "time_limit_ms": 2000,
            "memory_limit_kb": 262144
        },
        "RTE"
    )
    
    # Test 4.5: Java - Runtime Error (NullPointerException)
    run_test(
        "Java - Runtime Error - NullPointerException",
        {
            "code": "public class Main {\n    public static void main(String[] args) {\n        String str = null;\n        System.out.println(str.length());\n    }\n}",
            "language": "java",
            "test_cases": [
                {"input": "", "expected_output": ""}
            ],
            "time_limit_ms": 2000,
            "memory_limit_kb": 262144
        },
        "RTE"
    )
    
    # Test 4.6: Java - Runtime Error (ArrayIndexOutOfBoundsException)
    run_test(
        "Java - Runtime Error - ArrayIndexOutOfBoundsException",
        {
            "code": "public class Main {\n    public static void main(String[] args) {\n        int[] arr = {1, 2, 3};\n        System.out.println(arr[10]);\n    }\n}",
            "language": "java",
            "test_cases": [
                {"input": "", "expected_output": ""}
            ],
            "time_limit_ms": 2000,
            "memory_limit_kb": 262144
        },
        "RTE"
    )
    
    # Test 4.7: Java - Compilation Error
    run_test(
        "Java - Compilation Error (CE)",
        {
            "code": "public class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello\")\n    }\n}",
            "language": "java",
            "test_cases": [
                {"input": "", "expected_output": "Hello"}
            ],
            "time_limit_ms": 2000,
            "memory_limit_kb": 262144
        },
        "CE"
    )
    
    # ========================================================================
    # EDGE CASES
    # ========================================================================
    print_header("5. EDGE CASES")
    
    # Test 5.1: Empty Input
    run_test(
        "Empty Input",
        {
            "code": "print('Hello World')",
            "language": "python",
            "test_cases": [
                {"input": "", "expected_output": "Hello World"}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "AC"
    )
    
    # Test 5.2: Empty Output
    run_test(
        "Empty Output",
        {
            "code": "input()",
            "language": "python",
            "test_cases": [
                {"input": "test", "expected_output": ""}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "AC"
    )
    
    # Test 5.3: Multiple Lines Output
    run_test(
        "Multiple Lines Output",
        {
            "code": "n = int(input())\nfor i in range(1, n+1):\n    print(i)",
            "language": "python",
            "test_cases": [
                {"input": "3", "expected_output": "1\n2\n3"},
                {"input": "5", "expected_output": "1\n2\n3\n4\n5"}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "AC"
    )
    
    # Test 5.4: Output Format with Extra Spaces
    run_test(
        "Output Format - Extra Spaces",
        {
            "code": "a, b = map(int, input().split())\nprint(a + b, ' ')",
            "language": "python",
            "test_cases": [
                {"input": "2 2", "expected_output": "4"},
                {"input": "5 5", "expected_output": "10"}
            ],
            "time_limit_ms": 1000,
            "memory_limit_kb": 262144
        },
        "AC"
    )
    
    # ========================================================================
    # PRINT SUMMARY
    # ========================================================================
    print_header("📊 TEST SUMMARY")
    
    total = stats["total"]
    passed = stats["passed"]
    failed = stats["failed"]
    errors = stats["errors"]
    skipped = stats["skipped"]
    
    print(f"Total Tests:   {total}")
    print(f"{Colors.OKGREEN}Passed:        {passed}{Colors.ENDC}")
    print(f"{Colors.FAIL}Failed:        {failed}{Colors.ENDC}")
    print(f"{Colors.WARNING}Errors:        {errors}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Skipped:       {skipped}{Colors.ENDC}")
    
    if passed > 0:
        success_rate = (passed / (total - skipped)) * 100 if (total - skipped) > 0 else 0
        print(f"\n{Colors.BOLD}Success Rate:  {success_rate:.2f}%{Colors.ENDC}")
    
    print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Exit code
    if failed > 0 or errors > 0:
        print(f"\n{Colors.FAIL}Some tests failed! 😞{Colors.ENDC}")
        exit(1)
    else:
        print(f"\n{Colors.OKGREEN}All tests passed! 🎉{Colors.ENDC}")
        exit(0)

if __name__ == "__main__":
    main()
