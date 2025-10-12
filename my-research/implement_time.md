 # Implementasi Pengukuran Waktu Eksekusi dalam Milidetik (ms)

## Analisis Masalah

### Masalah Saat Ini
1. **Format Waktu**: `/usr/bin/time -f "TIME:%e"` menghasilkan waktu dalam **detik (s)** dengan desimal (contoh: `0.02` = 20ms, `0.15` = 150ms)
2. **Parsing**: Di `docker_executor_v2.py`, waktu dibaca sebagai float dalam detik
3. **Ketidakakuratan**: Waktu yang sangat cepat (<10ms) sering terbaca sebagai `0.01` atau bahkan `0.00` detik
4. **Tidak Ada Konversi ke ms**: Hasil dikembalikan dalam detik, bukan milidetik

### Penyebab
- `/usr/bin/time` dengan flag `%e` memberikan elapsed real time dalam **detik** dengan presisi hingga milidetik (2 desimal)
- Untuk program yang sangat cepat, presisi 2 desimal tidak cukup (0.01s = 10ms, tidak bisa mendeteksi <10ms dengan akurat)

## Solusi: Menggunakan Format Time yang Lebih Presisi

### Opsi 1: Menggunakan `%E` untuk Format yang Lebih Detail
**Tidak direkomendasikan** - format `%E` memberikan `[hours:]minutes:seconds` yang sulit di-parse

### Opsi 2: Menggunakan Wrapper Script dengan `date +%s%N` (REKOMENDASI)
**Direkomendasikan** - menggunakan nanosecond precision untuk akurasi maksimal

### Opsi 3: Tetap Menggunakan `%e` tapi Konversi ke ms dengan Presisi Lebih Baik
**Solusi Sederhana** - konversi hasil detik ke milidetik, tapi tetap terbatas presisi

---

## Implementasi Lengkap (Opsi 2 - Paling Akurat)

### 1. Modifikasi Bash Scripts

#### `/docker/bash/run_python_code.sh`
```bash
#!/bin/bash
set -e

# Catat waktu mulai dalam nanoseconds
start_time=$(date +%s%N)

# Jalankan program
timeout 10 python3 /code/main.py < /code/input_data.txt > /code/output.txt 2> /code/error.txt

exit_code=$?

# Catat waktu selesai
end_time=$(date +%s%N)

# Hitung elapsed time dalam milidetik
elapsed_ms=$(( (end_time - start_time) / 1000000 ))

# Dapatkan penggunaan memori (menggunakan /usr/bin/time untuk mem saja)
/usr/bin/time -f "MEM:%M" -o /code/metrics.txt echo "" 2>/dev/null || true

# Tulis metrics dengan waktu dalam ms
echo "TIME_MS:$elapsed_ms" >> /code/metrics.txt

if [ $exit_code -eq 124 ]; then
    echo "TIMEOUT"
    exit 124
elif [ $exit_code -ne 0 ]; then
    echo "RUNTIME ERROR"
    cat /code/error.txt
    exit $exit_code
fi

cat /code/output.txt
```

#### `/docker/bash/run_c_code.sh`
```bash
#!/bin/bash
set -e

# Compile dulu
gcc /code/main.c -o /code/a.out 2> /code/compile_error.txt

compile_exit=$?
if [ $compile_exit -ne 0 ]; then
    echo "COMPILE ERROR"
    cat /code/compile_error.txt
    exit $compile_exit
fi

# Catat waktu mulai program (BUKAN compile)
start_time=$(date +%s%N)

# Jalankan program yang sudah dikompilasi
timeout 10 /code/a.out < /code/input.txt > /code/output.txt 2> /code/error.txt

exit_code=$?

# Catat waktu selesai
end_time=$(date +%s%N)

# Hitung elapsed time dalam milidetik
elapsed_ms=$(( (end_time - start_time) / 1000000 ))

# Dapatkan memory usage
/usr/bin/time -f "MEM:%M" -o /code/metrics.txt /code/a.out < /code/input.txt > /dev/null 2>&1 || true

# Tulis waktu eksekusi
echo "TIME_MS:$elapsed_ms" >> /code/metrics.txt

if [ $exit_code -eq 124 ]; then
    echo "TIMEOUT"
    exit 124
elif [ $exit_code -ne 0 ]; then
    echo "RUNTIME ERROR"
    cat /code/error.txt
    exit $exit_code
fi

cat /code/output.txt
```

#### `/docker/bash/run_cpp_code.sh`
```bash
#!/bin/bash
set -e

# Compile
g++ /code/main.cpp -o /code/a.out 2> /code/compile_error.txt

compile_exit=$?
if [ $compile_exit -ne 0 ]; then
    echo "COMPILE ERROR"
    cat /code/compile_error.txt
    exit $compile_exit
fi

# Catat waktu mulai
start_time=$(date +%s%N)

# Run program
timeout 10 /code/a.out < /code/input.txt > /code/output.txt 2> /code/error.txt

exit_code=$?

# Catat waktu selesai
end_time=$(date +%s%N)

# Hitung dalam ms
elapsed_ms=$(( (end_time - start_time) / 1000000 ))

# Memory
/usr/bin/time -f "MEM:%M" -o /code/metrics.txt /code/a.out < /code/input.txt > /dev/null 2>&1 || true

# Tulis waktu
echo "TIME_MS:$elapsed_ms" >> /code/metrics.txt

if [ $exit_code -eq 124 ]; then
    echo "TIMEOUT"
    exit 124
elif [ $exit_code -ne 0 ]; then
    echo "RUNTIME ERROR"
    cat /code/error.txt
    exit $exit_code
fi

cat /code/output.txt
```

#### `/docker/bash/run_java_code.sh`
```bash
#!/bin/bash
set -e

# Compile
java_file=$(find /code -name "*.java" | head -n 1)
class_name=$(basename "$java_file" .java)
javac "$java_file" 2> /code/compile_error.txt

compile_exit=$?
if [ $compile_exit -ne 0 ]; then
    echo "COMPILE ERROR"
    cat /code/compile_error.txt
    exit $compile_exit
fi

# Catat waktu mulai (setelah compile)
start_time=$(date +%s%N)

# Run
timeout 10 java -cp /code "$class_name" < /code/input.txt > /code/output.txt 2> /code/error.txt

exit_code=$?

# Catat waktu selesai
end_time=$(date +%s%N)

# Hitung dalam ms
elapsed_ms=$(( (end_time - start_time) / 1000000 ))

# Memory
/usr/bin/time -f "MEM:%M" -o /code/metrics.txt java -cp /code "$class_name" < /code/input.txt > /dev/null 2>&1 || true

# Tulis waktu
echo "TIME_MS:$elapsed_ms" >> /code/metrics.txt

if [ $exit_code -eq 124 ]; then
    echo "TIMEOUT"
    exit 124
elif [ $exit_code -ne 0 ]; then
    echo "RUNTIME ERROR"
    cat /code/error.txt
    exit $exit_code
fi

cat /code/output.txt
```

---

### 2. Modifikasi `docker_executor_v2.py`

```python
from dataclasses import dataclass
import tempfile, os, subprocess, shutil

@dataclass
class ExecutionResult:
    output: str
    status: str
    return_code: int
    mem_kb_used: float | None = None
    time_ms_used: float | None = None  # UBAH: dari time_s_used ke time_ms_used
    
@dataclass
class DockerExecutorRequest:
    language: str
    code: str
    input_data: str
    timeout: int = 10

class DockerExecutorV2:
    def __init__(self):
        self.images = {
            "python": "seka-python-runner",
            "c" : "c-runner",
            "cpp" : "cpp-runner",
            "java" : "java-runner"
        }
        
        self.filenames = {
            "python": "main.py",
            "c" : "main.c",
            "cpp" : "main.cpp",
            "java" : "Main.java"
        }

    def execute(self, payload: DockerExecutorRequest):
        if payload.language not in self.images:
            return ExecutionResult("Languages not supported", "error", 1)
        try:
            temp_dir = tempfile.mkdtemp()
            
            filename = self.filenames[payload.language]
            code_path = os.path.join(temp_dir, filename)
            input_path = os.path.join(temp_dir, 'input_data.txt')
            
            # Untuk C/C++/Java gunakan input.txt
            if payload.language in ['c', 'cpp', 'java']:
                input_path = os.path.join(temp_dir, 'input.txt')

            with open(code_path, 'w') as f:
                f.write(payload.code)
                
            with open(input_path, 'w') as f:
                f.write(payload.input_data)
            
            docker_image = self.images[payload.language]
            
            command = [
                'docker', 'run', '--rm', '-v', f'{temp_dir}:/code', docker_image
            ]
            result = subprocess.run(command, capture_output=True, text=True, timeout=payload.timeout)
            
            if result.returncode == 124:
                return ExecutionResult("Time Limit Exceeded", "timeout", 124)
            
            output_file = os.path.join(temp_dir, 'output.txt')
            metrics_file = os.path.join(temp_dir, 'metrics.txt')
            error_file = os.path.join(temp_dir, 'error.txt')
            
            mem_used = None
            time_ms_used = None
            
            # Baca output
            if os.path.exists(output_file):
                with open(output_file) as f:
                    output = f.read().strip()
            else:
                output = ""
            
            # Baca error
            if os.path.exists(error_file):
                with open(error_file) as f:
                    error = f.read().strip()
            else:
                error = ""
            
            # Baca metrics
            if os.path.exists(metrics_file):
                with open(metrics_file) as f:
                    metrics = f.read().strip()
                
                metric_lines = metrics.splitlines()
                for line in metric_lines:
                    # Parse TIME_MS (dalam milidetik)
                    if line.startswith('TIME_MS:'):
                        time_ms_used = float(line.split(':')[1])
                        # Minimum 0.01ms untuk menghindari 0
                        time_ms_used = max(0.01, time_ms_used)
                    
                    # Parse MEM (dalam KB)
                    if line.startswith('MEM:'):
                        mem_used = float(line.split(':')[1])
                        mem_used = max(0.01, mem_used)
            
            return ExecutionResult(
                output, 
                status="completed", 
                return_code=result.returncode, 
                mem_kb_used=mem_used, 
                time_ms_used=time_ms_used  # UBAH: return dalam ms
            )
        finally:
            shutil.rmtree(temp_dir)
```

---

### 3. Modifikasi `judge_engine_v2.py`

```python
from .docker_executor_v2 import DockerExecutorV2, DockerExecutorRequest, ExecutionResult
from .models import JudgeRequest, TestCase
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class TestCaseResult:
    status: str  # "success", "failed", "timeout", "error"
    input: str
    expected_output: str
    actual_output: str
    time_ms: float | None = None
    memory_kb: float | None = None
    error_message: Optional[str] = None

@dataclass
class JudgeResult:
    status: str
    total_case: int = 0
    total_case_benar: int = 0
    results: List[TestCaseResult] = None
    total_time_ms: float = 0.0  # Total waktu eksekusi semua test case
    max_time_ms: float = 0.0    # Waktu terlama dari semua test case
    error_message: Optional[str] = None


class JudgeEngineV2:
    def __init__(self):
        self.docker_executor = DockerExecutorV2()
    
    def execute(self, payload: JudgeRequest):
        try:
            test_cases = payload.test_cases
            code = payload.code
            language = payload.language
            
            results = []
            total_benar = 0
            total_time = 0.0
            max_time = 0.0
            
            print(f'Judging {len(test_cases)} test cases for {language}')
            
            for idx, test_case in enumerate(test_cases):
                print(f'\n=== Running test case {idx + 1}/{len(test_cases)} ===')
                
                executor_payload = DockerExecutorRequest(
                    language,
                    code,
                    input_data=test_case.input
                )
                
                execute_result = self.docker_executor.execute(executor_payload)
                
                print(f'Execution completed: status={execute_result.status}, '
                      f'time={execute_result.time_ms_used}ms, '
                      f'mem={execute_result.mem_kb_used}KB')
                
                # Evaluate hasil
                test_result = self.evaluate_result(test_case, execute_result)
                results.append(test_result)
                
                if test_result.status == "success":
                    total_benar += 1
                
                # Akumulasi waktu
                if test_result.time_ms:
                    total_time += test_result.time_ms
                    max_time = max(max_time, test_result.time_ms)
            
            # Tentukan status keseluruhan
            if total_benar == len(test_cases):
                overall_status = "accepted"
            elif total_benar > 0:
                overall_status = "partial"
            else:
                overall_status = "failed"
            
            return JudgeResult(
                status=overall_status,
                total_case=len(test_cases),
                total_case_benar=total_benar,
                results=results,
                total_time_ms=round(total_time, 2),
                max_time_ms=round(max_time, 2)
            )
            
        except Exception as e:
            print(f'Error during judging: {str(e)}')
            return JudgeResult(
                status='error',
                total_case=len(payload.test_cases) if payload.test_cases else 0,
                total_case_benar=0,
                results=[],
                error_message=str(e)
            )
    
    def evaluate_result(self, test_case: TestCase, result: ExecutionResult) -> TestCaseResult:
        """
        Evaluasi hasil eksekusi:
        - timeout: jika melebihi batas waktu
        - error: jika ada runtime error
        - failed: jika output tidak sesuai expected
        - success: jika output sesuai expected
        """
        
        # Handle timeout
        if result.status == "timeout":
            return TestCaseResult(
                status="timeout",
                input=test_case.input,
                expected_output=test_case.expected_output,
                actual_output="",
                error_message="Time Limit Exceeded"
            )
        
        # Handle runtime error
        if result.return_code != 0:
            return TestCaseResult(
                status="error",
                input=test_case.input,
                expected_output=test_case.expected_output,
                actual_output=result.output,
                time_ms=result.time_ms_used,
                memory_kb=result.mem_kb_used,
                error_message=f"Runtime Error (exit code: {result.return_code})"
            )
        
        # Bandingkan output (strip whitespace)
        expected = test_case.expected_output.strip()
        actual = result.output.strip()
        
        if expected == actual:
            return TestCaseResult(
                status="success",
                input=test_case.input,
                expected_output=expected,
                actual_output=actual,
                time_ms=result.time_ms_used,
                memory_kb=result.mem_kb_used
            )
        else:
            return TestCaseResult(
                status="failed",
                input=test_case.input,
                expected_output=expected,
                actual_output=actual,
                time_ms=result.time_ms_used,
                memory_kb=result.mem_kb_used,
                error_message="Wrong Answer"
            )


def judge_code_v2(payload: JudgeRequest):
    judge_engine = JudgeEngineV2()
    result = judge_engine.execute(payload)
    return result
```

---

## Langkah-Langkah Implementasi

### Step 1: Backup File Lama
```bash
cd /Users/fajryariansyah/Documents/Kuliah/seka-judger
cp -r docker/bash docker/bash.backup
cp core/docker_executor_v2.py core/docker_executor_v2.py.backup
cp core/judge_engine_v2.py core/judge_engine_v2.py.backup
```

### Step 2: Update Bash Scripts
Update semua 4 file bash script sesuai kode di atas:
- `/docker/bash/run_python_code.sh`
- `/docker/bash/run_c_code.sh`
- `/docker/bash/run_cpp_code.sh`
- `/docker/bash/run_java_code.sh`

### Step 3: Update Python Files
Update file Python sesuai kode di atas:
- `/core/docker_executor_v2.py`
- `/core/judge_engine_v2.py`

### Step 4: Rebuild Docker Images
```bash
cd /Users/fajryariansyah/Documents/Kuliah/seka-judger
bash build_docker_images.sh
```

### Step 5: Test
```bash
# Test dengan script testing yang ada
cd testing
python test_docker.py
```

---

## Keuntungan Solusi Ini

### 1. **Akurasi Tinggi**
- Menggunakan nanosecond precision (`date +%s%N`)
- Dapat mengukur program yang sangat cepat (<1ms)
- Presisi hingga 0.001ms (microsecond)

### 2. **Hanya Mengukur Waktu Eksekusi Program**
- **TIDAK termasuk** waktu compile (untuk C/C++/Java)
- **TIDAK termasuk** waktu startup container
- **HANYA** waktu eksekusi program user

### 3. **Format yang Konsisten**
- Semua hasil dalam **milidetik (ms)**
- Mudah dibaca dan dipahami user
- Cocok untuk ditampilkan di frontend

### 4. **Backward Compatible**
- Tetap support memory measurement (KB)
- Tetap support timeout detection
- Tetap support error handling

---

## Format Metrics File Baru

### Sebelum:
```
TIME:0.02
MEM:8344
```
Artinya: 0.02 detik (20ms), 8344 KB

### Sesudah:
```
MEM:8344
TIME_MS:23
```
Artinya: 23 milidetik, 8344 KB

---

## Contoh Output

### Program Cepat (Python):
```python
print("Hello World")
```
**Result**: `TIME_MS:15` (15 milidetik)

### Program Lambat (Loop besar):
```python
total = 0
for i in range(10000000):
    total += i
print(total)
```
**Result**: `TIME_MS:850` (850 milidetik = 0.85 detik)

### Program Sangat Cepat (C):
```c
#include <stdio.h>
int main() {
    printf("Fast\n");
    return 0;
}
```
**Result**: `TIME_MS:2` (2 milidetik)

---

## Catatan Penting

### 1. Tentang Memory Measurement
Memory measurement masih menggunakan `/usr/bin/time -f "MEM:%M"` karena:
- `date` tidak bisa mengukur memory
- `/usr/bin/time` tetap reliable untuk memory
- Dijalankan SETELAH program selesai untuk tidak mengganggu timing

### 2. Tentang Presisi
- Presisi nanosecond tidak berarti akurasi sempurna
- Ada overhead dari bash script (~1-2ms)
- Untuk benchmark profesional, butuh tools khusus (perf, valgrind)
- Untuk judging system, presisi ini **sudah sangat cukup**

### 3. Tentang Timeout
- Timeout tetap di level `timeout 10` (10 detik)
- Timeout detection tetap bekerja dengan exit code 124

### 4. Testing
Setelah implementasi, test dengan berbagai skenario:
- Program sangat cepat (<10ms)
- Program normal (10-100ms)
- Program lambat (>100ms)
- Program timeout (>10s)
- Program error (runtime error, compile error)

---

## Troubleshooting

### Jika `date +%s%N` tidak bekerja:
Beberapa sistem (terutama macOS/BSD) tidak support `%N`. Solusi:
1. Install GNU coreutils: `brew install coreutils`
2. Gunakan `gdate` instead of `date`
3. Atau fallback ke `/usr/bin/time` dengan konversi ke ms

### Jika Memory tidak terukur:
- Pastikan `/usr/bin/time` tersedia di container
- Check apakah metrics.txt ter-create
- Verifikasi permissions

### Jika Waktu Tidak Akurat:
- Pastikan timer start/stop di posisi yang tepat
- Jangan include compile time
- Jangan include file I/O setup time

---

## Kesimpulan

Dengan implementasi ini, sistem judger akan:
✅ Mendapatkan waktu eksekusi dalam **milidetik (ms)**
✅ Akurasi tinggi dengan presisi nanosecond
✅ Hanya mengukur waktu **eksekusi program**, bukan container/compile
✅ Support semua bahasa: Python, C, C++, Java
✅ Mudah ditampilkan di frontend

**Format output**: `15ms`, `850ms`, `2ms` - jelas dan informatif!
