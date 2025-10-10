# SEKA Judger 🚀

Sistem Online Judge berbasis web untuk menjalankan dan menguji kode pemrograman secara otomatis. Mendukung multiple bahasa pemrograman dengan Docker containerization untuk keamanan.

## 📋 Fitur Utama

- ✅ **Multi-Language Support**: C, C++, Java, Python
- ⚡ **Real-time Code Execution**: Compile dan execute code secara real-time
- 🧪 **Automated Test Cases**: Testing otomatis dengan multiple test cases
- 🔒 **Docker Isolation**: Eksekusi kode dalam container untuk keamanan
- 🎨 **Web Interface**: UI modern dengan code editor (Ace Editor)
- 📊 **Detailed Results**: Hasil eksekusi lengkap dengan execution time
- 🛡️ **Timeout Protection**: Proteksi dari infinite loops
- 🔍 **Error Detection**: Compile error, runtime error, dan timeout detection

## 🏗️ Arsitektur

```
seka-judger/
├── main.py                 # FastAPI application entry point
├── core/
│   ├── compiler.py         # Compiler abstraction untuk setiap bahasa
│   ├── executor.py         # Code execution engine
│   ├── judge_engine.py     # Core judging logic
│   ├── models.py           # Pydantic models
│   └── config.py           # Configuration
├── templates/              # HTML templates
├── static/                 # CSS & JavaScript files
├── docker/                 # Dockerfiles untuk setiap bahasa
└── tests/                  # Test files
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker (untuk deployment)
- GCC/G++ (untuk C/C++)
- Java JDK 17+ (untuk Java)

### Instalasi

1. **Clone repository**
```bash
git clone https://github.com/Papazy/seka-judger.git
cd seka-judger
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Jalankan server**
```bash
fastapi dev main.py
```

Server akan berjalan di `http://localhost:8000`

### Docker Deployment

1. **Build Docker image**
```bash
docker build -t seka-judger .
```

2. **Run container**
```bash
docker run -p 8001:8001 seka-judger
```

Server akan berjalan di `http://localhost:8001`

## 📖 Tutorial Penggunaan

### 1. Menggunakan Web Interface

1. Buka browser dan akses `http://localhost:8000`
2. Pilih bahasa pemrograman dari dropdown
3. Tulis kode di editor
4. Tambahkan test cases dengan klik tombol "Add"
5. Isi input dan expected output untuk setiap test case
6. Klik "Run Code" untuk execute
7. Lihat hasil di bagian Results

### 2. Menggunakan API Endpoint

#### POST /judge

Menjalankan dan menilai kode pemrograman.

**Request Body:**
```json
{
  "code": "#include <stdio.h>\nint main() { int a; scanf(\"%d\", &a); printf(\"%d\", a*2); return 0; }",
  "language": "c",
  "test_cases": [
    {
      "input": "2",
      "expected_output": "4"
    },
    {
      "input": "5",
      "expected_output": "10"
    }
  ]
}
```

**Response:**
```json
{
  "status": "finished",
  "total_case": 2,
  "total_case_benar": 2,
  "results": [
    {
      "input": "2",
      "expected_output": "4",
      "actual_output": "4",
      "passed": true,
      "status": "accepted",
      "execution_time": 0.023
    },
    {
      "input": "5",
      "expected_output": "10",
      "actual_output": "10",
      "passed": true,
      "status": "accepted",
      "execution_time": 0.021
    }
  ]
}
```

### 3. Contoh Penggunaan dengan cURL

```bash
curl -X POST "http://localhost:8000/judge" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "#include <iostream>\nusing namespace std;\nint main() { int a; cin >> a; cout << a*2; return 0; }",
    "language": "cpp",
    "test_cases": [
      {"input": "3", "expected_output": "6"}
    ]
  }'
```

### 4. Contoh Penggunaan dengan Python

```python
import requests

url = "http://localhost:8000/judge"
payload = {
    "code": "a = int(input())\nprint(a * 2)",
    "language": "python",
    "test_cases": [
        {"input": "4", "expected_output": "8"},
        {"input": "10", "expected_output": "20"}
    ]
}

response = requests.post(url, json=payload)
print(response.json())
```

### 5. Contoh Kode untuk Setiap Bahasa

#### C
```c
#include <stdio.h>
int main() {
    int a;
    scanf("%d", &a);
    printf("%d", a * 2);
    return 0;
}
```

#### C++
```cpp
#include <iostream>
using namespace std;
int main() {
    int a;
    cin >> a;
    cout << a * 2;
    return 0;
}
```

#### Java
```java
import java.util.Scanner;
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        System.out.print(a * 2);
    }
}
```

#### Python
```python
a = int(input())
print(a * 2)
```

## 🔧 Supported Languages

| Language | Compiler/Interpreter | Version |
|----------|---------------------|---------|
| C        | GCC                 | Latest  |
| C++      | G++                 | Latest  |
| Java     | OpenJDK             | 17+     |
| Python   | Python3             | 3.12+   |

## 📊 Status Response

| Status | Deskripsi |
|--------|-----------|
| `accepted` | Kode berhasil dan output sesuai |
| `failed` | Kode berjalan tapi output salah |
| `compile_error` | Error saat kompilasi |
| `runtime_error` | Error saat eksekusi |
| `timeout` | Eksekusi melebihi batas waktu (5 detik) |
| `system_error` | Error sistem internal |

## 🧪 Running Tests

```bash
pytest test_judge_endpoint.py -v
```

## ⚙️ Konfigurasi

### Timeout Settings

Edit di `core/executor.py`:
```python
class CodeExecutor:
    def __init__(self, timeout: int=5):  # ubah nilai timeout (detik)
        self.timeout = timeout
```

### Compiler Settings

Edit di `core/compiler.py` untuk custom compiler flags.

## 🔐 Keamanan

- **Docker Isolation**: Kode dijalankan dalam container terpisah
- **Timeout Protection**: Batas waktu eksekusi untuk mencegah infinite loops
- **Resource Limits**: Pembatasan memory dan CPU usage (dalam Docker)
- **File System Isolation**: Temporary files untuk setiap session

## 📡 API Endpoints

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/` | GET | Web interface |
| `/judge` | POST | Submit dan judge kode |
| `/health` | GET | Health check endpoint |

## 🐛 Troubleshooting

### Error: "gcc: command not found"
Install GCC/G++:
```bash
# Ubuntu/Debian
sudo apt-get install gcc g++

# MacOS
brew install gcc
```

### Error: "javac: command not found"
Install Java JDK:
```bash
# Ubuntu/Debian
sudo apt-get install openjdk-17-jdk

# MacOS
brew install openjdk@17
```

### Timeout terlalu cepat
Edit timeout di `core/executor.py` dan `core/compiler.py`.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

**Papazy**
- GitHub: [@Papazy](https://github.com/Papazy)

## 🙏 Acknowledgments

- FastAPI untuk web framework
- Ace Editor untuk code editor
- Docker untuk containerization
- Tailwind CSS untuk styling

---

Made with ❤️ for education purposes
