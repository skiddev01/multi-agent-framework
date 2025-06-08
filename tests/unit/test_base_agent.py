"""Tests for base agent functionality"""

import pytest
from unittest.mock import Mock
from src.agents.base_agent import BaseAgent, AgentConfig

@pytest.fixture
def sample_config():
    return AgentConfig(
        name="test_agent",
        role="Test Agent",
        goal="Test agent functionality",
        backstory="A test agent for unit testing",
        tools=["test_tool"],
        memory_enabled=True
    )

class TestAgent(BaseAgent):
    def execute(self, task: str, context=None):
        return {"status": "success", "result": f"Executed: {task}"}

@pytest.fixture
def test_agent(sample_config):
    return TestAgent(sample_config)

def test_agent_initialization(test_agent, sample_config):
    """Test agent is properly initialized"""
    assert test_agent.config.name == "test_agent"
    assert test_agent.config.role == "Test Agent"
    assert test_agent.memory == {}
    assert test_agent.execution_history == []

def test_agent_execute(test_agent):
    """Test agent execution"""
    result = test_agent.execute("test task")
    
    assert result["status"] == "success"
    assert "test task" in result["result"]

def test_agent_memory_update(test_agent):
    """Test memory functionality"""
    test_agent.update_memory("key1", "value1")
    
    assert test_agent.memory["key1"] == "value1"

def test_agent_execution_logging(test_agent):
    """Test execution is logged"""
    test_agent.execute("test task")
    
    assert len(test_agent.execution_history) == 1
    assert test_agent.execution_history[0]["task"] == "test task"

def test_agent_capabilities(test_agent):
    """Test agent capabilities reporting"""
    capabilities = test_agent.get_capabilities()
    
    assert "test_tool" in capabilities
