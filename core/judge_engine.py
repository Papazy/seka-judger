

from .models import JudgeRequest, TestCase
from typing import Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .compiler import CompilerFactory, JavaCompiler
from .executor import CodeExecutor
from typing import Optional



from dataclasses import dataclass

import uuid
import os
import glob


@dataclass
class JudgeResult:
  status: str
  total_case : int = 0
  total_case_benar : int = 0
  result : dict = None
  error_message: Optional[str] = None

class JudgeEngine:
  def __init__(self):
    self.executor = CodeExecutor(timeout=5)
    self.compiler_factory = CompilerFactory()
    
  def judge_code(self, payload: JudgeRequest):
    session_id = str(uuid.uuid4())
    
    # mendapatkan compiler
    try:
      compiler = self.compiler_factory.get_compiler(payload.language)
      
      if isinstance(compiler, JavaCompiler):
        compiler.set_session(session_id)
      # compile
      compilation_result = compiler.compile(payload.code, session_id)
      print(f"mendapatkan compile: ", compilation_result)
      
      if not compilation_result.success:
        return JudgeResult(
          status="compile_error",
          total_case=0,
          total_case_benar=0,
          result=[],
          error_message=compilation_result.error_message
        )
        
      # execute test cases
      results = []
      total_passed = 0
      
      for test_case in payload.test_cases:
        command = compiler.get_execution_command(compilation_result.executable_path)
        
        execution_result = self.executor.execute(command, test_case.input)
        
        is_passed = self._validate_output(
          execution_result.output, 
          test_case.expected_output
        )
        
        if is_passed:
          total_passed += 1
          
        if execution_result.status == "timeout":
          final_status = "timeout"
        elif execution_result.status == "runtime_error":
          final_status = "runtime_error"
        elif execution_result.status == "execution_error":
          final_status = "execution_error"
        elif is_passed:
          final_status = "accepted"
        else:
          final_status = "failed"
          
        results.append({
          "input": test_case.input,
          "expected_output": test_case.expected_output,
          "actual_output": execution_result.output,
          "passed": is_passed,
          "status": final_status,
          "execution_time": execution_result.execution_time
        })
      
      return {
        "status": "finished",
        "total_case": len(payload.test_cases),
        "total_case_benar" : total_passed,
        "results" : results
      }
    except Exception as e:
      return {
        "status": "system_error",
        "total_case": len(payload.test_cases),
        "total_case_benar": 0,
        "results": [],
        "error_message": str(e)
      }
    finally:
      # Cleanup temporary files
      self._cleanup_session_files(session_id)
      
  def _validate_output(self, actual, expected):
    actual_normalized = actual.replace("\r\n", "\n")
    expected_normalized = expected.replace("\r\n", "\n")
    
    return actual_normalized == expected_normalized
      
  def _cleanup_session_files(self, session_id):
    patterns = [
      f"temp/{session_id}.*",
      f"temp/*.class" # untk java
    ]
    
    for pattern in patterns:
      for file_path in glob.glob(pattern):
        try:
          if os.path.isfile(file_path):
            os.remove(file_path)
        except OSError:
          pass
        
def judge_code(payload: JudgeRequest):
  engine = JudgeEngine()
  return engine.judge_code(payload)


# def compile_code(filename, binary_filename, language):
#   if language == 'c':
#     command = ["gcc", filename, "-o", binary_filename]
#   elif language == 'c++' or language == 'cpp':
#     command = ["g++", filename, "-o", binary_filename]
  
#   try:
#     subprocess.run(command, check=True, capture_output=True)
#     return "berhasil"
#   except subprocess.CalledProcessError as e:
#     return "gagal"
  

# def judge_code_with_test_case(binary_filename, tc):
#   process = subprocess.run([binary_filename], input=tc.input.encode(), capture_output=True, timeout=5)
#   output = process.stdout.decode().strip()
#   expected =  tc.expected_output.strip()
  
#   output = normalize_output(output)
#   expected = normalize_output(expected)
  
#   if process.returncode != 0:
#     status = "runtime_error"
#   elif output == expected:
#     status = "accepted"
#   elif output != expected:
#     status = "failed"

#   return status, expected, output
  

# def judge_code(payload: JudgeRequest):
#   # generate a unique ID for the request
#   session_id = str(uuid.uuid4())
#   filename = f"temp/{session_id}.{'c' if payload.language == 'c' else 'cpp'}"
#   binary_filename = f"temp/{session_id}.out"
  
#   jumlah_soal = 0
#   jumlah_benar = 0
  
#   # menyimpan kode ke file
#   with open(filename, "w") as f:
#       f.write(payload.code)
  
#   # mengkompilasi kode
#   compile_status = compile_code(filename, binary_filename, payload.language)
#   if(compile_status == "gagal"): 
#     return {
#       "session_id" : session_id, 
#       "status" : "compile_error",
#       "message" : e.stderr.decode(),
#       'results' : []
#     }
  
#   # test setiap test case
#   results = []
#   for tc in payload.test_cases:
#     try:
#       status, expected, output = judge_code_with_test_case(binary_filename, tc)

#       # kalau berhasil
#       results.append({
#           "input": tc.input,
#           "expected_output": expected,
#           "actual_output": output,
#           "passed": output == expected,
#           "status": status
#       })
      
#     #kalau error timeout
#     except subprocess.TimeoutExpired:
#       status = "timeout"
#       results.append({
#           "input": tc.input,
#           "expected_output": tc.expected_output,
#           "actual_output": "Timeout",
#           "passed": False,
#           "status": status
#       })
#     except Exception as e:
#       print("Error:", e)
#       status = "unknown_error"
#       results.append({
#         "input": tc.input,
#           "expected_output": tc.expected_output,
#           "actual_output": "error",
#           "passed": False,
#           "status": "unknown_error"
#       })
#     finally:
#       if status == "accepted":
#         jumlah_benar += 1
#       jumlah_soal += 1
  

#   try:
#     os.remove(filename)
#     os.remove(binary_filename)
#   except:
#     pass
  
  
#   return {
#       "session_id": session_id,
#       "status" : "finished",
#       "total_case" : jumlah_soal,
#       "total_case_benar" : jumlah_benar,
#       "results": results
#   }
            
            
    
# # Fungsi untuk normalisasi output (terkadang output "\r\n" yang mana maknanya sama aja dengan "\n")
# def normalize_output(output: str) -> str:
#     return output.replace("\r\n", "\n").strip()
