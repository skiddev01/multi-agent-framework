"""Base agent class following four-level design methodology"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class AgentLevel(str, Enum):
    CONCEPTUAL = "conceptual"
    FUNCTIONAL = "functional" 
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"

class AgentConfig(BaseModel):
    """Configuration for agent instances"""
    name: str
    role: str
    goal: str
    backstory: str
    tools: List[str] = Field(default_factory=list)
    memory_enabled: bool = True
    max_iterations: int = 5
    llm_model: str = "gpt-4-turbo"
    verbose: bool = False

class BaseAgent(ABC):
    """Base class for all multi-agent framework agents"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.memory: Dict[str, Any] = {}
        self.execution_history: List[Dict[str, Any]] = []
        
    @abstractmethod
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a task - must be implemented by subclasses"""
        pass
        
    def log_execution(self, task: str, result: Dict[str, Any]) -> None:
        """Log execution for monitoring and debugging"""
        self.execution_history.append({
            "task": task,
            "result": result,
            "timestamp": self._get_timestamp()
        })
        
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
        
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return self.config.tools
        
    def update_memory(self, key: str, value: Any) -> None:
        """Update agent memory"""
        if self.config.memory_enabled:
            self.memory[key] = value
