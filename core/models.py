from pydantic import BaseModel
from enum import Enum
from typing import List

class LanguageEnum (str, Enum):
  C = "c"
  CPP = "cpp"
  JAVA = "java"
  PYTHON = "python"


class TestCase(BaseModel):
  input: str
  expected_output: str
  
class JudgeRequest(BaseModel):
  code: str
  test_cases: List[TestCase]
  language: str = "c"
  
