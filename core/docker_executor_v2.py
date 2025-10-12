from dataclasses import dataclass
import tempfile, os, subprocess, shutil

@dataclass
class ExecutionResult:
    output: str
    status: str  # "completed", "timeout", "error", "compilation_error"
    return_code: int
    mem_kb_used: float | None = None
    time_ms_used: float | None = None
    error_output: str = ""  # Stderr output
    compilation_error: str = ""  # Compilation error message
    
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
            "c" : "seka-c-runner",
            "cpp" : "seka-cpp-runner",
            "java" : "seka-java-runner"
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
            print("Result execute", result)
            if result.returncode == 124:
                return ExecutionResult("Time Limit Exceeded", "timeout", 124)
            
            # Check for compilation error first
            compile_error_file = os.path.join(temp_dir, 'compile_error.txt')
            status_file = os.path.join(temp_dir, 'status.txt')
            status_execution="SUCCESS"
            # Status execution
            if os.path.exists(status_file):
                print("STATUS FILE EXIST")
                print("RETURN CODE", result.returncode)
                print("res")
                with open(status_file) as f:
                    print("STATUS EXECUTION", f.read())
                    status_execution = f.read().strip()

            print('status_execution: ', status_execution)
            if os.path.exists(compile_error_file):
                print('compile_error_file', compile_error_file)
                
                with open(compile_error_file) as f:
                    compile_error = f.read().strip()
                    print('compile_error', compile_error)
                    if compile_error and (status_execution == "COMPILE_ERROR" or result.returncode != 0):
                        return ExecutionResult(
                            "",
                            status="COMPILE_ERROR",
                            return_code=1,
                            compilation_error=compile_error
                        )
            
            output_file = os.path.join(temp_dir, 'output.txt')
            metrics_file = os.path.join(temp_dir, 'metrics.txt')
            error_file = os.path.join(temp_dir, 'error.txt')
            mem_used = None
            time_used = None
            error_output = ""
            
            # Read output
            if os.path.exists(output_file):
                with open(output_file) as f:
                    output = f.read().strip()
            else:
                output = ""
            
            # Read metrics
            if os.path.exists(metrics_file):
                with open(metrics_file) as f:
                    metrics = f.read().strip()
            else:
                metrics = ""
                
            # Read error
            if os.path.exists(error_file):
                with open(error_file) as f:
                    print("ERROR in file", f.read())
                    error_output = f.read().strip()
            if error_output or result.stderr:
                status_execution = "RUNTIME_ERROR"
                print('result.stderr', result.stderr)
                error_output = result.stderr if result.stderr else error_output
                
            # Parse metrics
            metric_lines = metrics.splitlines()
            for line in metric_lines:
                if line.startswith('MEM:'):
                    mem_used = float(f"{float(line.split(':')[1]):.2f}")
                    mem_used = max(0.01, mem_used)  # Minimum 0.01 KB

                if line.startswith('TIME:'):
                    time_used = float(line.split(':')[1])
                    time_used = max(0.01, time_used)  # Minimum 0.01 ms

                
            # print('time_used', time_used)
            # print("mem_used", mem_used)
            
            return ExecutionResult(
                output, 
                status=status_execution, 
                return_code=result.returncode, 
                mem_kb_used=mem_used, 
                time_ms_used=time_used,
                error_output=error_output
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                "",
                status="TIMEOUT",
                return_code=124,
                error_output="Process timed out"
            )
        except Exception as e:
            print("ERROR di Execute", e)
            return ExecutionResult(
                "",
                status="ERROR",
                return_code=1,
            )
        finally:
            shutil.rmtree(temp_dir)
        
        