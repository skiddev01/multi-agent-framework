"""Configuration management for multi-agent systems"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from dotenv import load_dotenv

class EnvironmentConfig(BaseModel):
    """Environment-specific configuration"""
    name: str
    llm_models: Dict[str, str]
    max_iterations: int
    timeout_seconds: int
    monitoring_enabled: bool
    log_level: str

class AgentDefinition(BaseModel):
    """Agent definition from configuration"""
    name: str
    role: str
    goal: str
    backstory: str
    tools: List[str]
    memory_enabled: bool = True

class ConfigManager:
    """Centralized configuration management"""
    
    def __init__(self, environment: str = "development"):
        load_dotenv()
        self.environment = environment
        self.config_path = Path("src/config")
        self._load_configurations()
        
    def _load_configurations(self) -> None:
        """Load all configuration files"""
        # Load environment config
        env_file = self.config_path / "environments" / f"{self.environment}.yaml"
        if env_file.exists():
            with open(env_file, encoding='utf-8') as f:
                env_data = yaml.safe_load(f)
                self.env_config = EnvironmentConfig(**env_data)
        else:
            # Default configuration
            self.env_config = EnvironmentConfig(
                name=self.environment,
                llm_models={"default": "gpt-4-turbo"},
                max_iterations=5,
                timeout_seconds=300,
                monitoring_enabled=True,
                log_level="INFO"
            )
            
        # Load agent definitions
        self.agents = self._load_agent_definitions()
        
    def _load_agent_definitions(self) -> Dict[str, AgentDefinition]:
        """Load agent definitions from configuration"""
        agents_file = self.config_path / "agents.yaml"
        if not agents_file.exists():
            return {}
            
        with open(agents_file, encoding='utf-8') as f:
            agents_data = yaml.safe_load(f)
            
        return {
            name: AgentDefinition(**config)
            for name, config in agents_data.get("agents", {}).items()
        }
        
    def get_agent_config(self, agent_name: str) -> Optional[AgentDefinition]:
        """Get configuration for specific agent"""
        return self.agents.get(agent_name)
        
    def get_api_key(self, service: str) -> str:
        """Get API key for service"""
        key_name = f"{service.upper()}_API_KEY"
        key = os.getenv(key_name)
        if not key:
            raise ValueError(f"Missing API key: {key_name}")
        return key
        
    def get_llm_model(self, agent_name: str = "default") -> str:
        """Get LLM model for agent"""
        return self.env_config.llm_models.get(agent_name, self.env_config.llm_models["default"])
