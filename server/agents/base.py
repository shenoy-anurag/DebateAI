from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

import config


@dataclass
class AgentResponse:
    content: str
    citations: list[str]
    metadata: Dict[str, Any] = None


class BaseAgent(ABC):
    def __init__(
        self,
        system_prompt: str,
        model_name: str = None,
        temperature: float = 0.7
    ):
        self.system_prompt = system_prompt
        self.model_name = model_name or config.OPENAI_MODEL
        self.temperature = temperature
        
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=config.OPENAI_API_KEY,
        )
        
        self.messages = [SystemMessage(content=system_prompt)]

    @abstractmethod
    def process(self, input_text: str, **kwargs) -> AgentResponse:
        pass

    def _call_llm(self, prompt: str) -> str:
        self.messages.append(HumanMessage(content=prompt))
        
        response = self.llm.invoke(self.messages)
        
        self.messages.append(AIMessage(content=response.content))
        
        return response.content

    def reset(self):
        self.messages = [SystemMessage(content=self.system_prompt)]
