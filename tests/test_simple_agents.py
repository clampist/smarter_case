"""
Tests for simple agents implementation.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.agents.simple_agents import (
    code_analysis_agent,
    requirement_analysis_agent,
    test_selection_agent as select_test_agent,
    reflection_agent,
    execution_agent
)


class TestCodeAnalysisAgent:
    """Test cases for code analysis agent."""
    
    @patch('src.agents.simple_agents.client')
    def test_code_analysis_agent_success(self, mock_client):
        """Test successful code analysis."""
        # Mock the client response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"commit_hash": "abc123", "files_changed": ["src/test.py"]}'
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test the agent
        result = code_analysis_agent("abc123", "main")
        
        # Assertions
        assert result["agent"] == "code_analysis_agent"
        assert result["status"] == "completed"
        assert "abc123" in result["input"]["commit_hash"]
        assert result["output"] is not None
    
    @patch('src.agents.simple_agents.client')
    def test_code_analysis_agent_failure(self, mock_client):
        """Test code analysis agent failure handling."""
        # Mock the client to raise an exception
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        # Test the agent with a real model to force AI call instead of mock
        result = code_analysis_agent("abc123", "main", model="openai:gpt-4o")
        
        # Assertions
        assert result["agent"] == "code_analysis_agent"
        assert result["status"] == "failed"
        assert "Error: API Error" in result["output"]


class TestRequirementAnalysisAgent:
    """Test cases for requirement analysis agent."""
    
    @patch('src.agents.simple_agents.client')
    def test_requirement_analysis_agent_success(self, mock_client):
        """Test successful requirement analysis."""
        # Mock the client response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"requirement_changes": [{"id": "REQ-123"}]}'
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test the agent
        result = requirement_analysis_agent("24h", "PROJ")
        
        # Assertions
        assert result["agent"] == "requirement_analysis_agent"
        assert result["status"] == "completed"
        assert result["input"]["time_range"] == "24h"
        assert result["input"]["project_key"] == "PROJ"


class TestTestSelectionAgent:
    """Test cases for test selection agent."""
    
    @patch('src.agents.simple_agents.client')
    def test_test_selection_agent_success(self, mock_client):
        """Test successful test selection."""
        # Mock the client response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"selected_tests": {"api_tests": []}}'
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test data
        code_analysis = {"output": '{"files_changed": ["src/api.py"]}'}
        requirement_analysis = {"output": '{"requirement_changes": []}'}
        
        # Test the agent
        result = select_test_agent(code_analysis, requirement_analysis)
        
        # Assertions
        assert result["agent"] == "test_selection_agent"
        assert result["status"] == "completed"
        assert "code_analysis" in result["input"]
        assert "requirement_analysis" in result["input"]


class TestReflectionAgent:
    """Test cases for reflection agent."""
    
    @patch('src.agents.simple_agents.client')
    def test_reflection_agent_success(self, mock_client):
        """Test successful reflection."""
        # Mock the client response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"optimized_selection": {"api_tests": []}}'
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test data
        test_selection = {"output": '{"selected_tests": {"api_tests": []}}'}
        
        # Test the agent
        result = reflection_agent(test_selection)
        
        # Assertions
        assert result["agent"] == "reflection_agent"
        assert result["status"] == "completed"
        assert "test_selection" in result["input"]


class TestExecutionAgent:
    """Test cases for execution agent."""
    
    @patch('src.agents.simple_agents.client')
    def test_execution_agent_success(self, mock_client):
        """Test successful execution command generation."""
        # Mock the client response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"execution_commands": {"setup": []}}'
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test data
        optimized_selection = {"output": '{"optimized_selection": {"api_tests": []}}'}
        
        # Test the agent
        result = execution_agent(optimized_selection, "github-actions")
        
        # Assertions
        assert result["agent"] == "execution_agent"
        assert result["status"] == "completed"
        assert result["input"]["ci_cd_platform"] == "github-actions"


if __name__ == "__main__":
    pytest.main([__file__])
