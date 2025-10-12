# Test Cases untuk Judge API

Gunakan endpoint: `POST http://localhost:8000/v2/judge`

## 1. Python Tests

### ✅ Test 1.1: Python - All Accepted (AC)
```json
{
  "code": "a, b = map(int, input().split())\nprint(a + b)",
  "language": "python",
  "test_cases": [
    { "input": "2 2", "expected_output": "4" },
    { "input": "5 5", "expected_output": "10" },
    { "input": "3 3", "expected_output": "6" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: AC, Score: 100

---

### ❌ Test 1.2: Python - Wrong Answer (WA)
```json
{
  "code": "a, b = map(int, input().split())\nprint(a * b)",
  "language": "python",
  "test_cases": [
    { "input": "2 2", "expected_output": "4" },
    { "input": "5 5", "expected_output": "10" },
    { "input": "3 3", "expected_output": "6" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: WA (multiply instead of add, hanya test case 1 yang benar)

---

### ⏱️ Test 1.3: Python - Time Limit Exceeded (TLE)
```json
{
  "code": "while True:\n    pass",
  "language": "python",
  "test_cases": [
    { "input": "", "expected_output": "" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: TLE

---

### 💥 Test 1.4: Python - Runtime Error (RE) - Division by Zero
```json
{
  "code": "print(1 / 0)",
  "language": "python",
  "test_cases": [
    { "input": "", "expected_output": "" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: RE

---

### 💥 Test 1.5: Python - Runtime Error (RE) - Index Out of Range
```json
{
  "code": "arr = [1, 2, 3]\nprint(arr[10])",
  "language": "python",
  "test_cases": [
    { "input": "", "expected_output": "" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: RE

---

### 🔨 Test 1.6: Python - Syntax Error (akan jadi RE karena Python tidak dikompilasi)
```json
{
  "code": "print('Hello World'",
  "language": "python",
  "test_cases": [
    { "input": "", "expected_output": "Hello World" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: RE (syntax error saat runtime)

---

### ✅ Test 1.7: Python - Partial Accepted
```json
{
  "code": "a, b = map(int, input().split())\nif a == 2:\n    print(a + b)\nelse:\n    print(a * b)",
  "language": "python",
  "test_cases": [
    { "input": "2 2", "expected_output": "4" },
    { "input": "5 5", "expected_output": "10" },
    { "input": "3 3", "expected_output": "6" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: WA, Score: 33.33 (hanya test case 1 yang benar)

---

## 2. C Tests

### ✅ Test 2.1: C - All Accepted (AC)
```json
{
  "code": "#include <stdio.h>\nint main() {\n    int a, b;\n    scanf(\"%d %d\", &a, &b);\n    printf(\"%d\\n\", a + b);\n    return 0;\n}",
  "language": "c",
  "test_cases": [
    { "input": "2 2", "expected_output": "4" },
    { "input": "5 5", "expected_output": "10" },
    { "input": "3 3", "expected_output": "6" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: AC, Score: 100

---

### ❌ Test 2.2: C - Wrong Answer (WA)
```json
{
  "code": "#include <stdio.h>\nint main() {\n    int a, b;\n    scanf(\"%d %d\", &a, &b);\n    printf(\"%d\\n\", a * b);\n    return 0;\n}",
  "language": "c",
  "test_cases": [
    { "input": "2 2", "expected_output": "4" },
    { "input": "5 5", "expected_output": "10" },
    { "input": "3 3", "expected_output": "6" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: WA

---

### ⏱️ Test 2.3: C - Time Limit Exceeded (TLE)
```json
{
  "code": "#include <stdio.h>\nint main() {\n    while(1) {}\n    return 0;\n}",
  "language": "c",
  "test_cases": [
    { "input": "", "expected_output": "" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: TLE

---

### 💥 Test 2.4: C - Runtime Error (RE) - Division by Zero
```json
{
  "code": "#include <stdio.h>\nint main() {\n    int x = 5 / 0;\n    printf(\"%d\\n\", x);\n    return 0;\n}",
  "language": "c",
  "test_cases": [
    { "input": "", "expected_output": "" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: RE

---

### 💥 Test 2.5: C - Runtime Error (RE) - Segmentation Fault
```json
{
  "code": "#include <stdio.h>\nint main() {\n    int *ptr = NULL;\n    printf(\"%d\\n\", *ptr);\n    return 0;\n}",
  "language": "c",
  "test_cases": [
    { "input": "", "expected_output": "" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: RE

---

### 🔨 Test 2.6: C - Compilation Error (CE)
```json
{
  "code": "#include <stdio.h>\nint main() {\n    printf(\"Hello World\"\n    return 0;\n}",
  "language": "c",
  "test_cases": [
    { "input": "", "expected_output": "Hello World" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: CE (missing semicolon and closing parenthesis)

---

### 🔨 Test 2.7: C - Compilation Error (CE) - Undefined Function
```json
{
  "code": "#include <stdio.h>\nint main() {\n    undefinedFunction();\n    return 0;\n}",
  "language": "c",
  "test_cases": [
    { "input": "", "expected_output": "" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: CE

---

## 3. C++ Tests

### ✅ Test 3.1: C++ - All Accepted (AC)
```json
{
  "code": "#include <iostream>\nusing namespace std;\nint main() {\n    int a, b;\n    cin >> a >> b;\n    cout << a + b << endl;\n    return 0;\n}",
  "language": "cpp",
  "test_cases": [
    { "input": "2 2", "expected_output": "4" },
    { "input": "5 5", "expected_output": "10" },
    { "input": "3 3", "expected_output": "6" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: AC, Score: 100

---

### ❌ Test 3.2: C++ - Wrong Answer (WA)
```json
{
  "code": "#include <iostream>\nusing namespace std;\nint main() {\n    int a, b;\n    cin >> a >> b;\n    cout << a - b << endl;\n    return 0;\n}",
  "language": "cpp",
  "test_cases": [
    { "input": "5 3", "expected_output": "8" },
    { "input": "10 5", "expected_output": "15" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: WA (subtraction instead of addition)

---

### ⏱️ Test 3.3: C++ - Time Limit Exceeded (TLE)
```json
{
  "code": "#include <iostream>\nusing namespace std;\nint main() {\n    while(true) {}\n    return 0;\n}",
  "language": "cpp",
  "test_cases": [
    { "input": "", "expected_output": "" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: TLE

---

### 💥 Test 3.4: C++ - Runtime Error (RE) - Out of Bounds
```json
{
  "code": "#include <iostream>\n#include <vector>\nusing namespace std;\nint main() {\n    vector<int> v = {1, 2, 3};\n    cout << v[100] << endl;\n    return 0;\n}",
  "language": "cpp",
  "test_cases": [
    { "input": "", "expected_output": "" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: RE atau WA (undefined behavior)

---

### 💥 Test 3.5: C++ - Runtime Error (RE) - Exception
```json
{
  "code": "#include <iostream>\n#include <stdexcept>\nusing namespace std;\nint main() {\n    throw runtime_error(\"Error!\");\n    return 0;\n}",
  "language": "cpp",
  "test_cases": [
    { "input": "", "expected_output": "" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: RE

---

### 🔨 Test 3.6: C++ - Compilation Error (CE)
```json
{
  "code": "#include <iostream>\nusing namespace std;\nint main() {\n    cout << \"Hello\" << end;\n    return 0;\n}",
  "language": "cpp",
  "test_cases": [
    { "input": "", "expected_output": "Hello" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: CE (should be 'endl' not 'end')

---

### 🔨 Test 3.7: C++ - Compilation Error (CE) - Missing Semicolon
```json
{
  "code": "#include <iostream>\nusing namespace std;\nint main() {\n    int x = 5\n    cout << x << endl;\n    return 0;\n}",
  "language": "cpp",
  "test_cases": [
    { "input": "", "expected_output": "5" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: CE

---

## 4. Java Tests

### ✅ Test 4.1: Java - All Accepted (AC)
```json
{
  "code": "import java.util.Scanner;\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int a = sc.nextInt();\n        int b = sc.nextInt();\n        System.out.println(a + b);\n        sc.close();\n    }\n}",
  "language": "java",
  "test_cases": [
    { "input": "2 2", "expected_output": "4" },
    { "input": "5 5", "expected_output": "10" },
    { "input": "3 3", "expected_output": "6" }
  ],
  "time_limit_ms": 2000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: AC, Score: 100

---

### ❌ Test 4.2: Java - Wrong Answer (WA)
```json
{
  "code": "import java.util.Scanner;\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int a = sc.nextInt();\n        int b = sc.nextInt();\n        System.out.println(a * b);\n        sc.close();\n    }\n}",
  "language": "java",
  "test_cases": [
    { "input": "2 2", "expected_output": "4" },
    { "input": "5 5", "expected_output": "10" },
    { "input": "3 3", "expected_output": "6" }
  ],
  "time_limit_ms": 2000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: WA

---

### ⏱️ Test 4.3: Java - Time Limit Exceeded (TLE)
```json
{
  "code": "public class Main {\n    public static void main(String[] args) {\n        while(true) {}\n    }\n}",
  "language": "java",
  "test_cases": [
    { "input": "", "expected_output": "" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: TLE

---

### 💥 Test 4.4: Java - Runtime Error (RE) - Division by Zero
```json
{
  "code": "public class Main {\n    public static void main(String[] args) {\n        int x = 5 / 0;\n        System.out.println(x);\n    }\n}",
  "language": "java",
  "test_cases": [
    { "input": "", "expected_output": "" }
  ],
  "time_limit_ms": 2000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: RE (ArithmeticException)

---

### 💥 Test 4.5: Java - Runtime Error (RE) - NullPointerException
```json
{
  "code": "public class Main {\n    public static void main(String[] args) {\n        String str = null;\n        System.out.println(str.length());\n    }\n}",
  "language": "java",
  "test_cases": [
    { "input": "", "expected_output": "" }
  ],
  "time_limit_ms": 2000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: RE (NullPointerException)

---

### 💥 Test 4.6: Java - Runtime Error (RE) - ArrayIndexOutOfBoundsException
```json
{
  "code": "public class Main {\n    public static void main(String[] args) {\n        int[] arr = {1, 2, 3};\n        System.out.println(arr[10]);\n    }\n}",
  "language": "java",
  "test_cases": [
    { "input": "", "expected_output": "" }
  ],
  "time_limit_ms": 2000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: RE (ArrayIndexOutOfBoundsException)

---

### 🔨 Test 4.7: Java - Compilation Error (CE) - Missing Semicolon
```json
{
  "code": "public class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello\")\n    }\n}",
  "language": "java",
  "test_cases": [
    { "input": "", "expected_output": "Hello" }
  ],
  "time_limit_ms": 2000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: CE

---

### 🔨 Test 4.8: Java - Compilation Error (CE) - Wrong Class Name
```json
{
  "code": "public class WrongName {\n    public static void main(String[] args) {\n        System.out.println(\"Hello\");\n    }\n}",
  "language": "java",
  "test_cases": [
    { "input": "", "expected_output": "Hello" }
  ],
  "time_limit_ms": 2000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: CE atau RE (class name harus Main)

---

## 5. Advanced Test Cases

### 💾 Test 5.1: Memory Limit Exceeded (MLE) - Python
```json
{
  "code": "arr = [0] * (1024 * 1024 * 1024)\nprint(len(arr))",
  "language": "python",
  "test_cases": [
    { "input": "", "expected_output": "1073741824" }
  ],
  "time_limit_ms": 5000,
  "memory_limit_kb": 10240
}
```
**Expected**: Verdict: MLE atau RE

---

### 💾 Test 5.2: Memory Limit Exceeded (MLE) - C++
```json
{
  "code": "#include <iostream>\n#include <vector>\nusing namespace std;\nint main() {\n    vector<int> v(1024 * 1024 * 1024);\n    cout << v.size() << endl;\n    return 0;\n}",
  "language": "cpp",
  "test_cases": [
    { "input": "", "expected_output": "1073741824" }
  ],
  "time_limit_ms": 5000,
  "memory_limit_kb": 10240
}
```
**Expected**: Verdict: MLE atau RE

---

### ✅ Test 5.3: Multiple Test Cases - Some Pass, Some Fail
```json
{
  "code": "import sys\na, b = map(int, input().split())\nif a < 10:\n    print(a + b)\nelse:\n    print(a * b)",
  "language": "python",
  "test_cases": [
    { "input": "2 3", "expected_output": "5" },
    { "input": "5 5", "expected_output": "10" },
    { "input": "10 5", "expected_output": "15" },
    { "input": "3 7", "expected_output": "10" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: WA, Score: 75 (3 out of 4 passed)

---

### ✅ Test 5.4: Output Format - Extra Spaces (Should Still Pass)
```json
{
  "code": "a, b = map(int, input().split())\nprint(a + b, ' ')",
  "language": "python",
  "test_cases": [
    { "input": "2 2", "expected_output": "4" },
    { "input": "5 5", "expected_output": "10" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: AC (trailing spaces ignored)

---

### ✅ Test 5.5: Multiple Lines Output
```json
{
  "code": "n = int(input())\nfor i in range(1, n+1):\n    print(i)",
  "language": "python",
  "test_cases": [
    { "input": "3", "expected_output": "1\n2\n3" },
    { "input": "5", "expected_output": "1\n2\n3\n4\n5" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: AC, Score: 100

---

### ✅ Test 5.6: Per-Test Case Time Limit
```json
{
  "code": "import time\nn = int(input())\ntime.sleep(n / 1000)\nprint(n)",
  "language": "python",
  "test_cases": [
    { 
      "input": "100", 
      "expected_output": "100",
      "time_limit_ms": 500
    },
    { 
      "input": "200", 
      "expected_output": "200",
      "time_limit_ms": 1000
    }
  ],
  "time_limit_ms": 2000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: AC (per-test time limits)

---

## 6. Edge Cases

### Test 6.1: Empty Input
```json
{
  "code": "print('Hello World')",
  "language": "python",
  "test_cases": [
    { "input": "", "expected_output": "Hello World" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: AC

---

### Test 6.2: Empty Output
```json
{
  "code": "input()",
  "language": "python",
  "test_cases": [
    { "input": "test", "expected_output": "" }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: AC

---

### Test 6.3: Large Input/Output
```json
{
  "code": "print(input())",
  "language": "python",
  "test_cases": [
    { 
      "input": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
      "expected_output": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
    }
  ],
  "time_limit_ms": 1000,
  "memory_limit_kb": 262144
}
```
**Expected**: Verdict: AC

---

## Cara Menggunakan

### 1. Menggunakan curl
```bash
curl -X POST http://localhost:8000/v2/judge \
  -H "Content-Type: application/json" \
  -d '{
    "code": "a, b = map(int, input().split())\nprint(a + b)",
    "language": "python",
    "test_cases": [
      { "input": "2 2", "expected_output": "4" }
    ],
    "time_limit_ms": 1000,
    "memory_limit_kb": 262144
  }'
```

### 2. Menggunakan Postman
1. Method: POST
2. URL: `http://localhost:8000/v2/judge`
3. Headers: `Content-Type: application/json`
4. Body: Raw JSON (copy dari contoh di atas)

### 3. Menggunakan Python requests
```python
import requests
import json

url = "http://localhost:8000/v2/judge"
payload = {
    "code": "a, b = map(int, input().split())\nprint(a + b)",
    "language": "python",
    "test_cases": [
        { "input": "2 2", "expected_output": "4" }
    ],
    "time_limit_ms": 1000,
    "memory_limit_kb": 262144
}

response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2))
```

---

## Response Format

Semua test akan mengembalikan response dengan format:

```json
{
  "verdict": "AC",
  "score": 100.0,
  "total_cases": 3,
  "passed_cases": 3,
  "total_time_ms": 45.23,
  "max_time_ms": 18.50,
  "avg_time_ms": 15.08,
  "max_memory_kb": 2048.00,
  "test_results": [
    {
      "case_number": 1,
      "verdict": "AC",
      "time_ms": 12.34,
      "memory_kb": 1024.00,
      "input_data": "2 2",
      "expected_output": "4",
      "actual_output": "4",
      "error_message": null
    }
  ],
  "error_message": null,
  "judged_at": "2025-10-12T10:30:45.123456"
}
```

---

## Verdict Types

- **AC** (Accepted): ✅ Semua test case passed
- **WA** (Wrong Answer): ❌ Output tidak sesuai expected
- **TLE** (Time Limit Exceeded): ⏱️ Waktu eksekusi melebihi batas
- **MLE** (Memory Limit Exceeded): 💾 Memory usage melebihi batas
- **RE** (Runtime Error): 💥 Program crash saat runtime
- **CE** (Compilation Error): 🔨 Kode tidak bisa dikompilasi

---

## Tips Testing

1. **Start Simple**: Mulai dengan test case AC sederhana untuk memastikan sistem bekerja
2. **Test Each Verdict**: Test satu per satu jenis verdict (AC, WA, TLE, RE, CE, MLE)
3. **Test Each Language**: Pastikan semua 4 bahasa bekerja dengan baik
4. **Check Metrics**: Perhatikan time_ms dan memory_kb untuk setiap test
5. **Edge Cases**: Test dengan input kosong, output kosong, dan input/output besar
6. **Concurrent Testing**: Test multiple request bersamaan untuk check stability

---

## Notes

- Java biasanya butuh time limit lebih besar (2000ms) karena JVM startup overhead
- Memory limit default adalah 256MB (262144 KB)
- Time limit per test case bisa di-override dengan `time_limit_ms` di TestCase
- Trailing spaces dan newlines di-ignore saat compare output
- Token-based comparison digunakan untuk numeric output
