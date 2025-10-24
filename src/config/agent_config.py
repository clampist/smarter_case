"""
Global configuration for agents and models.
"""
import os
from typing import Dict, Any


class AgentConfig:
    """Global configuration for agents."""
    
    # Default models for different providers
    DEFAULT_MODELS = {
        "openai": "openai:gpt-4o",
        "anthropic": "anthropic:claude-3-5-sonnet-20241022",
        "google": "google_rest:gemini-2.5-flash",  # Using custom aisuite with REST API (latest free model)
        "default": "mock"  # Default fallback to mock for testing
    }
    
    # Current active model
    ACTIVE_MODEL = os.getenv("ACTIVE_MODEL", DEFAULT_MODELS["default"])
    
    # Agent-specific configurations
    AGENT_CONFIGS = {
        "code_analysis": {
            "model": ACTIVE_MODEL,
            "temperature": 0.1,
            "max_tokens": 2000,
            "timeout": 300
        },
        "requirement_analysis": {
            "model": ACTIVE_MODEL,
            "temperature": 0.1,
            "max_tokens": 2000,
            "timeout": 300
        },
        "test_selection": {
            "model": ACTIVE_MODEL,
            "temperature": 0.2,
            "max_tokens": 3000,
            "timeout": 300
        },
        "reflection": {
            "model": ACTIVE_MODEL,
            "temperature": 0.3,
            "max_tokens": 3000,
            "timeout": 300
        },
        "execution": {
            "model": ACTIVE_MODEL,
            "temperature": 0.1,
            "max_tokens": 3000,
            "timeout": 300
        }
    }
    
    # CI/CD platform configurations
    CI_CD_PLATFORMS = {
        "github-actions": {
            "name": "GitHub Actions",
            "config_file": ".github/workflows/test.yml",
            "environment_vars": ["GITHUB_TOKEN", "TEST_RESULTS"]
        },
        "jenkins": {
            "name": "Jenkins",
            "config_file": "Jenkinsfile",
            "environment_vars": ["JENKINS_URL", "JENKINS_TOKEN"]
        }
    }
    
    @classmethod
    def get_agent_config(cls, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent."""
        return cls.AGENT_CONFIGS.get(agent_name, cls.AGENT_CONFIGS["code_analysis"])
    
    @classmethod
    def get_model_for_agent(cls, agent_name: str) -> str:
        """Get the model for a specific agent."""
        config = cls.get_agent_config(agent_name)
        return config["model"]
    
    @classmethod
    def get_temperature_for_agent(cls, agent_name: str) -> float:
        """Get the temperature for a specific agent."""
        config = cls.get_agent_config(agent_name)
        return config["temperature"]
    
    @classmethod
    def get_max_tokens_for_agent(cls, agent_name: str) -> int:
        """Get the max tokens for a specific agent."""
        config = cls.get_agent_config(agent_name)
        return config["max_tokens"]
