import sys
import os
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.llm_factory import LLMFactory, LLMProviderType

llm = LLMFactory.create_llm(LLMProviderType.DEEPSEEK)   
print(llm.complete("你好"))
