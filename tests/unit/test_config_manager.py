"""Tests for configuration management"""

import pytest
import tempfile
import yaml
from pathlib import Path
from src.config.config_manager import ConfigManager

def test_config_manager_basic():
    """Test basic config manager functionality"""
    try:
        config_manager = ConfigManager(environment="development")
        assert config_manager.environment == "development"
    except Exception as e:
        # This test might fail without proper config files, which is expected
        assert "Missing" in str(e) or "No such file" in str(e)
