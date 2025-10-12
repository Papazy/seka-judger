# Test Runner untuk Judge API

Script otomatis untuk menjalankan semua test case yang ada di `test.md`.

## Prerequisites

1. **Server harus running**:
   ```bash
   uvicorn main:app --reload
   ```

2. **Install dependencies**:
   ```bash
   pip install requests
   ```

## Cara Menjalankan

### Option 1: Jalankan semua tests
```bash
python run_all_tests.py
```

### Option 2: Make executable dan jalankan
```bash
chmod +x run_all_tests.py
./run_all_tests.py
```

## Output

Test runner akan menampilkan:
- ✅ **Hijau**: Test passed
- ❌ **Merah**: Test failed
- ⚠️ **Kuning**: Test skipped atau warning
- ℹ️ **Biru**: Informasi

### Contoh Output:
```
============================================================
🚀 Starting Judge API Test Suite
============================================================

ℹ Target: http://localhost:8000/v2/judge
ℹ Started at: 2025-10-12 10:30:45
✓ Server is running!

============================================================
1. PYTHON TESTS
============================================================

1. Python - All Accepted (AC)
ℹ Sending request to http://localhost:8000/v2/judge...
ℹ Elapsed time: 0.45s
ℹ Verdict: AC | Score: 100/100 | Passed: 3/3
ℹ Max Time: 15.23ms | Max Memory: 1024.00KB
✓ PASS - Got expected verdict: AC

2. Python - Wrong Answer (WA)
ℹ Sending request to http://localhost:8000/v2/judge...
ℹ Elapsed time: 0.38s
ℹ Verdict: WA | Score: 33.33/100 | Passed: 1/3
ℹ Max Time: 12.45ms | Max Memory: 1024.00KB
✓ PASS - Got expected verdict: WA

...

============================================================
📊 TEST SUMMARY
============================================================

Total Tests:   35
Passed:        30
Failed:        2
Errors:        0
Skipped:       3

Success Rate:  93.75%

Finished at: 2025-10-12 10:35:12

✓ Most tests passed! 🎉
```

## Test Categories

Script ini menjalankan test untuk:

### 1. Python Tests (7 tests)
- ✅ All Accepted
- ❌ Wrong Answer
- ⏱️ Time Limit Exceeded (skipped)
- 💥 Runtime Error (Division by Zero, Index Out of Range)
- 🔨 Syntax Error

### 2. C Tests (7 tests)
- ✅ All Accepted
- ❌ Wrong Answer
- ⏱️ Time Limit Exceeded (skipped)
- 💥 Runtime Error (Division by Zero, Segmentation Fault)
- 🔨 Compilation Error

### 3. C++ Tests (6 tests)
- ✅ All Accepted
- ❌ Wrong Answer
- ⏱️ Time Limit Exceeded (skipped)
- 💥 Runtime Error (Exception)
- 🔨 Compilation Error

### 4. Java Tests (7 tests)
- ✅ All Accepted
- ❌ Wrong Answer
- ⏱️ Time Limit Exceeded (skipped)
- 💥 Runtime Error (Division by Zero, NullPointer, ArrayIndexOutOfBounds)
- 🔨 Compilation Error

### 5. Edge Cases (4 tests)
- Empty Input
- Empty Output
- Multiple Lines Output
- Extra Spaces

**Total: ~35 tests** (excluding skipped tests)

## Skipped Tests

Tests yang **di-skip** (tidak dijalankan):
- ⏱️ **TLE tests** (Time Limit Exceeded) - karena memakan waktu lama (>10 detik per test)

Jika ingin menjalankan TLE tests, edit `run_all_tests.py` dan set `should_skip=False` pada test yang ingin dijalankan.

## Customization

### Menambah Test Baru

Edit `run_all_tests.py` dan tambahkan test baru:

```python
run_test(
    "Test Name",
    {
        "code": "your code here",
        "language": "python",
        "test_cases": [
            {"input": "input", "expected_output": "output"}
        ],
        "time_limit_ms": 1000,
        "memory_limit_kb": 262144
    },
    "AC"  # Expected verdict
)
```

### Mengubah Base URL

Jika server running di port lain:

```python
BASE_URL = "http://localhost:3000/v2/judge"
```

### Skip/Unskip Tests

Set `should_skip=True` atau `should_skip=False`:

```python
run_test(
    "Test Name",
    {...},
    "AC",
    should_skip=True  # Skip this test
)
```

## Troubleshooting

### Error: Cannot connect to server
```
✗ CONNECTION ERROR - Cannot connect to server
⚠ Make sure the server is running: uvicorn main:app --reload
```
**Solution**: Start the server first!

### Error: HTTP Error 500
```
✗ HTTP Error 500
```
**Solution**: Check server logs untuk error details.

### Error: Timeout
```
✗ TIMEOUT - Request took too long (>30s)
```
**Solution**: Increase timeout di `requests.post(..., timeout=30)` atau skip test tersebut.

### Tests Failed
Jika ada test yang failed, cek:
1. Apakah Docker images sudah di-build? (`bash build_docker_images.sh`)
2. Apakah bash scripts sudah benar? (check syntax error)
3. Apakah expected verdict benar?

## Exit Codes

- `0`: All tests passed ✅
- `1`: Some tests failed ❌

Berguna untuk CI/CD:
```bash
python run_all_tests.py
if [ $? -eq 0 ]; then
    echo "All tests passed!"
else
    echo "Tests failed!"
    exit 1
fi
```

## Performance

- **Fast tests** (AC, WA, RE, CE): ~0.3-1 second per test
- **Slow tests** (TLE, MLE): 10-30 seconds per test (di-skip by default)
- **Total runtime** (without TLE): ~2-5 minutes
- **Total runtime** (with TLE): ~10-20 minutes

## Tips

1. **Run quick tests first**: Tests yang di-skip adalah slow tests
2. **Parallel execution**: Untuk test yang banyak, bisa gunakan `concurrent.futures`
3. **Save results**: Output bisa di-pipe ke file: `python run_all_tests.py > results.txt`
4. **Focus on failed tests**: Jika ada yang failed, debug test tersebut dulu sebelum lanjut

## Example: Run with Output to File

```bash
python run_all_tests.py 2>&1 | tee test_results.txt
```

Akan save output ke `test_results.txt` sambil tetap print ke console.

## Contributing

Untuk menambah test case baru:
1. Tambahkan test case di `test.md`
2. Update `run_all_tests.py` dengan test case baru
3. Run test dan pastikan passed
4. Commit changes

---

Happy Testing! 🚀
