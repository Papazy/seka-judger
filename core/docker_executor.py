import docker
import os
import tempfile
import shutil
from typing import Optional
from dataclasses import dataclass
import re

@dataclass
class ExecutionResult:
    output: str
    status: str
    execution_time: Optional[float] = None
    memory_used: Optional[int] = None
    return_code: int = 0

class DockerExecutor:
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.client = docker.from_env()
        
        # Mapping bahasa ke image Docker
        self.image_map = {
            'c': 'seka-judger-c:latest',
            'cpp': 'seka-judger-cpp:latest',
            'java': 'seka-judger-java:latest',
            'python': 'seka-judger-python:latest'
        }
    
    def execute(self, language: str, code: str, input_data: str, session_id: str):
        """
        Execute code dalam Docker container
        
        Args:
            language: Bahasa pemrograman (c, cpp, java, python)
            code: Source code yang akan dieksekusi
            input_data: Input untuk program
            session_id: Unique session identifier
        
        Returns:
            ExecutionResult dengan output dan metrics
        """
        
        # Buat temporary directory untuk code dan data
        temp_dir = tempfile.mkdtemp(prefix=f"judger_{session_id}_")
        
        try:
            # Persiapan file berdasarkan bahasa
            self._prepare_files(temp_dir, language, code, input_data)
            
            # Dapatkan Docker image
            image_name = self.image_map.get(language)
            if not image_name:
                return ExecutionResult(
                    output="",
                    status="unsupported_language",
                    return_code=-1
                )
            
            # Jalankan container
            try:
                container = self.client.containers.run(
                    image=image_name,
                    volumes={temp_dir: {'bind': '/code', 'mode': 'rw'}},
                    network_mode='none',  # Isolasi network
                    mem_limit='256m',      # Limit memory
                    cpu_period=100000,
                    cpu_quota=50000,       # Limit CPU (50%)
                    detach=True,
                    remove=True,
                    user='runner'
                )
                
                # Tunggu execution selesai
                result = container.wait(timeout=self.timeout)
                
                # Baca output
                output = self._read_output(temp_dir)
                error_output = self._read_error(temp_dir)
                metrics = self._parse_metrics(temp_dir, language)
                
                # Determine status based on exit code and error
                if result['StatusCode'] != 0:
                    if error_output:
                        status = 'runtime_error'
                        output = error_output
                    else:
                        status = 'runtime_error'
                else:
                    status = 'completed'
                
                return ExecutionResult(
                    output=output,
                    status=status,
                    execution_time=metrics.get('time'),
                    memory_used=metrics.get('memory'),
                    return_code=result['StatusCode']
                )
                
            except docker.errors.ContainerError as e:
                error_output = self._read_error(temp_dir)
                return ExecutionResult(
                    output=error_output if error_output else str(e),
                    status='runtime_error',
                    return_code=e.exit_status
                )
            
            except Exception as e:
                error_msg = str(e)
                return ExecutionResult(
                    output=error_msg,
                    status='timeout' if 'timeout' in error_msg.lower() else 'execution_error',
                    return_code=-1
                )
                
        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _prepare_files(self, temp_dir: str, language: str, code: str, input_data: str):
        """Siapkan file code dan input"""
        
        # Tulis input data
        with open(os.path.join(temp_dir, 'input.txt'), 'w') as f:
            f.write(input_data)
        
        # Tulis source code
        if language == 'c':
            filename = 'main.c'
        elif language == 'cpp':
            filename = 'main.cpp'
        elif language == 'java':
            # Extract class name dari Java code
            match = re.search(r'public\s+class\s+(\w+)', code)
            class_name = match.group(1) if match else 'Main'
            filename = f'{class_name}.java'
        else:  # python
            filename = 'main.py'
        
        with open(os.path.join(temp_dir, filename), 'w') as f:
            f.write(code)
    
    def _read_output(self, temp_dir: str) -> str:
        """Baca output file"""
        output_file = os.path.join(temp_dir, 'output.txt')
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                return f.read().strip()
        return ""
    
    def _read_error(self, temp_dir: str) -> str:
        """Baca error file"""
        # Cek compile error
        compile_error = os.path.join(temp_dir, 'compile_error.txt')
        if os.path.exists(compile_error):
            with open(compile_error, 'r') as f:
                content = f.read().strip()
                if content:
                    return content
        
        # Cek runtime error
        runtime_error = os.path.join(temp_dir, 'runtime_error.txt')
        if os.path.exists(runtime_error):
            with open(runtime_error, 'r') as f:
                content = f.read().strip()
                if content:
                    return content
        
        # Cek general error
        error_file = os.path.join(temp_dir, 'error.txt')
        if os.path.exists(error_file):
            with open(error_file, 'r') as f:
                return f.read().strip()
        
        return ""
    
    def _parse_metrics(self, temp_dir: str, language: str) -> dict:
        """Parse execution metrics dari file"""
        metrics = {}
        
        # Tentukan file metrics berdasarkan bahasa
        if language == 'java':
            metrics_file = os.path.join(temp_dir, 'metrics_java.txt')
        else:
            metrics_file = os.path.join(temp_dir, 'metrics.txt')
        
        if os.path.exists(metrics_file):
            with open(metrics_file, 'r') as f:
                content = f.read()
                
                # Parse TIME
                time_match = re.search(r'TIME:(\d+\.\d+)', content)
                if time_match:
                    metrics['time'] = float(time_match.group(1))
                
                # Parse MEM
                mem_match = re.search(r'MEM:(\d+)', content)
                if mem_match:
                    metrics['memory'] = int(mem_match.group(1))
        
        return metrics
