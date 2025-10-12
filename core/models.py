from pydantic import BaseModel
from enum import Enum
from typing import List, Optional

class LanguageEnum(str, Enum):
  C = "c"
  CPP = "cpp"
  JAVA = "java"
  PYTHON = "python"

class Verdict(str, Enum):
  """Verdict standar untuk judging system"""
  ACCEPTED = "AC"
  WRONG_ANSWER = "WA"
  TIME_LIMIT_EXCEEDED = "TLE"
  MEMORY_LIMIT_EXCEEDED = "MLE"
  RUNTIME_ERROR = "RTE"
  COMPILATION_ERROR = "CE"
  PRESENTATION_ERROR = "PE"
  PENDING = "PENDING"
  JUDGING = "JUDGING"

class TestCase(BaseModel):
  input: str
  expected_output: str
  time_limit_ms: Optional[float] = 1000  # Default 1 second
  memory_limit_kb: Optional[float] = 256000  # Default 256 MB
  
class JudgeRequest(BaseModel):
  code: str
  test_cases: List[TestCase]
  language: str = "c"
  time_limit_ms: Optional[float] = 1000  # Global time limit
  memory_limit_kb: Optional[float] = 256000  # Global memory limit
  
