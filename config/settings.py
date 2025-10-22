"""
Application settings and configuration management.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "Smarter Case"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # AI Providers
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    
    # Jira Configuration
    jira_url: Optional[str] = Field(default=None, env="JIRA_URL")
    jira_username: Optional[str] = Field(default=None, env="JIRA_USERNAME")
    jira_api_token: Optional[str] = Field(default=None, env="JIRA_API_TOKEN")
    jira_project_key: Optional[str] = Field(default=None, env="JIRA_PROJECT_KEY")
    
    # Git Configuration
    git_repo_url: Optional[str] = Field(default=None, env="GIT_REPO_URL")
    git_branch: str = Field(default="main", env="GIT_BRANCH")
    git_access_token: Optional[str] = Field(default=None, env="GIT_ACCESS_TOKEN")
    
    # Database
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # CI/CD Configuration
    github_actions_token: Optional[str] = Field(default=None, env="GITHUB_ACTIONS_TOKEN")
    jenkins_url: Optional[str] = Field(default=None, env="JENKINS_URL")
    jenkins_username: Optional[str] = Field(default=None, env="JENKINS_USERNAME")
    jenkins_api_token: Optional[str] = Field(default=None, env="JENKINS_API_TOKEN")
    
    # Test Framework Configuration
    pytest_config_path: str = Field(default="./pytest.ini", env="PYTEST_CONFIG_PATH")
    playwright_config_path: str = Field(default="./playwright.config.js", env="PLAYWRIGHT_CONFIG_PATH")
    test_cases_db_path: str = Field(default="./data/test_cases/test_cases.json", env="TEST_CASES_DB_PATH")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    log_file_path: str = Field(default="./logs/application.log", env="LOG_FILE_PATH")
    
    # Performance
    max_concurrent_agents: int = Field(default=5, env="MAX_CONCURRENT_AGENTS")
    agent_timeout: int = Field(default=300, env="AGENT_TIMEOUT")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    
    # Security
    secret_key: Optional[str] = Field(default=None, env="SECRET_KEY")
    encryption_key: Optional[str] = Field(default=None, env="ENCRYPTION_KEY")
    
    # Monitoring
    prometheus_port: int = Field(default=8000, env="PROMETHEUS_PORT")
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
