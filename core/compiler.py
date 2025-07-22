from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass

import subprocess
import os
import logging


@dataclass
class CompilationResult:
  success: bool
  executable_path: Optional[str] = None
  error_message: Optional[str] = None

class BaseCompiler(ABC):
  def __init__(self, timeout: int = 10):
    self.timeout = timeout
    self.temp_dir = "temp"
    os.makedirs(self.temp_dir, exist_ok=True)
    
    @abstractmethod
    def compile(self, code, session_id):
      pass
    
    @abstractmethod
    def get_execution_command(self, executable_path):
      pass
    
    
class CCompiler(BaseCompiler):
  def __init__(self, language):
    super().__init__()
    self.language = language
    
  def compile(self, code, session_id):
    extension = "c" if self.language == "c" else "cpp"
    source_file = os.path.join(self.temp_dir, f"{session_id}.{extension}")
    executable_file = os.path.join(self.temp_dir, f"{session_id}.out")
    
    try:
      with open(source_file, "w") as f:
        f.write(code)
      
      if self.language == "c":
        command = ["gcc", source_file, "-o", executable_file]
      else : #cpp
        command = ["g++", source_file, "-o", executable_file]
      
      result = subprocess.run(
        command,
        capture_output=True,
        text = True,
      )
      
      if result.returncode == 0:
        return CompilationResult(success=True, executable_path=executable_file)
      else:
        
        return CompilationResult(success=False, error_message=result.stderr)
      
    except Exception as e:
      print(f"error ${e}")
      return CompilationResult(success=False, error_message=str(e))
    
    
  def get_execution_command(self, executable_path):
    return [executable_path]
    
    
    
class JavaCompiler(BaseCompiler):
  def __init__(self):
    super().__init__()
    self.language = "java"
    
  def compile(self, code, session_id):
    class_name = self._extract_class_name(code)
    
    if not class_name:
      return CompilationResult(success=False, error_message="No public class found")

    session_dir = os.path.join(self.temp_dir, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    print("session_dir, ", session_dir)
    
    source_file = os.path.join(session_dir, f"{class_name}.java")
    print("source_file, ", source_file)
    try:
      # Write source code
      with open(source_file, "w", encoding="utf-8") as f:
        f.write(code)
        
      command = ['javac', '-d', session_dir, source_file]
      print("command: ", command)
      result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=self.timeout,
      )
      
      
      if result.returncode == 0:
        return CompilationResult(success=True, executable_path=class_name)
      else:
        return CompilationResult(success=False, error_message=result.stderr)
    except Exception as e:
      return CompilationResult(success=False, error_message=str(e))
      

  def get_execution_command(self, executable_path):
    print(['java', '-cp', os.path.join(self.temp_dir, self._current_session_id), executable_path])
    return ['java', '-cp', os.path.join(self.temp_dir, self._current_session_id), executable_path]
  
  def set_session(self, session_id):
    self._current_session_id = session_id
  
  # Fungsi periksa class java
  @staticmethod
  def _extract_class_name(code):
    import re
    match = re.search(r'public\s+class\s+(\w+)', code)
    return match.group(1) if match else None
    
class PythonCompiler(BaseCompiler):
  def __init__(self):
    super().__init__()
    
  def compile(self, code, session_id):
    source_file = os.path.join(self.temp_dir, f"{session_id}.py")
    print("source_file", source_file)
    try:
      with open(source_file, "w", encoding="utf-8") as f:
        f.write(code)
        
      # command = ["python", "-m", "py_compile", source_file]
      # result = subprocess.run(
      #   command,
      #   capture_output=True,
      #   text=True,
      #   timeout=self.timeout
      # )
      # print("result :", result)
      # if result.returncode == 0:
        return CompilationResult(success=True, executable_path=source_file)
      # else:
        # return CompilationResult(success=False, error_message=result.stderr)
    except Exception as e:
      return CompilationResult(success=False, error_message=str(e))

    
  def get_execution_command(self, executable_path):
    return ["python", executable_path]
  
class CompilerFactory:
  @staticmethod
  def get_compiler(language: str) -> BaseCompiler:
    if language in ["c", "cpp", "c++"]:
      print('Get CCompiler')
      return CCompiler(language)
    elif language == "java":
      print('Get JavaCompiler')
      return JavaCompiler()
    elif language == "python":
      print('Get PythonCompiler')
      return PythonCompiler()
    else:
      raise ValueError(f"Unsupported language: {language}")