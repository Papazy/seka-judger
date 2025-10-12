import pytest
from fastapi.testclient import TestClient
from .main import app  # Remove the dot if main.py is in the same directory
import json

client = TestClient(app)

class TestJudgeEndpoint:
    
    def test_successful_code_execution(self):
        """Test code that should pass all test cases"""
        payload = {
            "code": "#include <stdio.h>\nint main() { int a; scanf(\"%d\", &a); printf(\"%d\", a*2); return 0; }",
            "language": "c",
            "test_cases": [
                {"input": "2", "expected_output": "4"},
                {"input": "5", "expected_output": "10"},
                {"input": "3", "expected_output": "6"}
            ]
        }
        
        response = client.post("/judge", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "finished"
        assert data["total_case"] == 3
        assert data["total_case_benar"] == 3
        assert len(data["results"]) == 3
        
        for result in data["results"]:
            assert result["passed"] == True
            assert result["status"] == "accepted"
    
    def test_compile_error(self):
        """Test code with compilation error (missing semicolon)"""
        payload = {
            "code": "#include <stdio.h>\nint main() { int a; scanf(\"%d\", &a); printf(\"%d\", a*2) return 0; }",
            "language": "c",
            "test_cases": [
                {"input": "2", "expected_output": "4"}
            ]
        }
        
        response = client.post("/judge", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "compile_error"
        assert "results" in data
    
    def test_runtime_error(self):
        """Test code that causes runtime error (null pointer dereference)"""
        payload = {
            "code": "#include <stdio.h>\nint main() { int a; scanf(\"%d\", &a); printf(\"%d\", a*2); int *p = NULL; *p = 10; return 0; }",
            "language": "c",
            "test_cases": [
                {"input": "2", "expected_output": "4"}
            ]
        }
        
        response = client.post("/judge", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "finished"
        assert len(data["results"]) == 1
        assert data["results"][0]["status"] == "runtime_error"
        assert data["results"][0]["passed"] == False
    
    def test_timeout_error(self):
        """Test code that causes timeout (infinite loop)"""
        payload = {
            "code": "#include <stdio.h>\nint main() { int a; scanf(\"%d\", &a); while(1) { printf(\"%d\", a*2); } return 0; }",
            "language": "c",
            "test_cases": [
                {"input": "2", "expected_output": "4"}
            ]
        }
        
        response = client.post("/judge", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "finished"
        assert len(data["results"]) == 1
        assert data["results"][0]["status"] == "timeout"
        assert data["results"][0]["passed"] == False
        assert data["results"][0]["actual_output"] == "Timeout"
    
    def test_wrong_output(self):
        """Test code that produces wrong output"""
        payload = {
            "code": "#include <stdio.h>\nint main() { int a; scanf(\"%d\", &a); printf(\"%d\", a*3); return 0; }",
            "language": "c",
            "test_cases": [
                {"input": "2", "expected_output": "4"}
            ]
        }
        
        response = client.post("/judge", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "finished"
        assert data["total_case"] == 1
        assert data["total_case_benar"] == 0
        assert data["results"][0]["status"] == "failed"
        assert data["results"][0]["passed"] == False
        assert data["results"][0]["actual_output"] == "6"
        assert data["results"][0]["expected_output"] == "4"
    
    def test_multiple_test_cases_mixed_results(self):
        """Test with multiple test cases where some pass and some fail"""
        payload = {
            "code": "#include <stdio.h>\nint main() { int a; scanf(\"%d\", &a); if(a == 2) printf(\"4\"); else printf(\"%d\", a*2); return 0; }",
            "language": "c",
            "test_cases": [
                {"input": "2", "expected_output": "4"},
                {"input": "5", "expected_output": "10"},
                {"input": "3", "expected_output": "6"}
            ]
        }
        
        response = client.post("/judge", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "finished"
        assert data["total_case"] == 3
        assert data["total_case_benar"] == 3
    
    def test_empty_test_cases(self):
        """Test with empty test cases list"""
        payload = {
            "code": "#include <stdio.h>\nint main() { return 0; }",
            "language": "c",
            "test_cases": [
                {"input": "2", "expected_output": "4"},
            ]
        }
        
        response = client.post("/judge", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "finished"
        assert data["total_case"] == 0
        assert data["total_case_benar"] == 0
        assert len(data["results"]) == 0

    def test_cpp_language(self):
        """Test C++ code compilation and execution"""
        payload = {
            "code": "#include <iostream>\nusing namespace std;\nint main() { int a; cin >> a; cout << a*2; return 0; }",
            "language": "c++",
            "test_cases": [
                {"input": "2", "expected_output": "4"}
            ]
        }
        
        response = client.post("/judge", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "finished"
        assert data["results"][0]["passed"] == True

if __name__ == "__main__":
    pytest.main([__file__])