import subprocess
import time

from typing import Optional
from dataclasses import dataclass

@dataclass
class ExecutionResult:
  output: str
  status: str
  execution_time: Optional[float] = None
  return_code: int = 0
  

class CodeExecutor:
  def __init__(self, timeout: int=5):
    self.timeout = timeout
    
  def execute(self, command, input_test_data):
    start_time = time.time()
    
    try:
      process = subprocess.run(
        command,
        input=input_test_data,
        capture_output=True,
        text=True,
        timeout=self.timeout,
      )
      
      execution_time = time.time() - start_time
      output = process.stdout.strip()
      
      if process.returncode != 0:
        error_output = process.stderr.strip()
        
        if error_output:
          status = "runtime_error"
          output = error_output
        else:
          status = "completed"
      else:
        status = "completed"
      
      return ExecutionResult(
        output=output,
        status=status,
        execution_time=execution_time,
        return_code=process.returncode
      )
    except subprocess.TimeoutExpired:
      return ExecutionResult(
        output="Timeout",
        status="timeout",
        execution_time=self.timeout
      )
  
    except Exception as e:
      return ExecutionResult(
        output=f"Execution error: {str(e)}",
        status="execution_error"
      )