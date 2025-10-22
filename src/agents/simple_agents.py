"""
Simple Agent implementations - unified import interface.
This module provides a unified interface to all agent implementations.
"""

# Import all agents from their individual modules
from .code_analysis_agent import code_analysis_agent_sync as code_analysis_agent
from .requirement_analysis_agent import requirement_analysis_agent_sync as requirement_analysis_agent
from .test_selection_agent import test_selection_agent
from .reflection_agent import reflection_agent
from .execution_agent import execution_agent

# Export all agents for easy importing
__all__ = [
    "code_analysis_agent",
    "requirement_analysis_agent", 
    "test_selection_agent",
    "reflection_agent",
    "execution_agent"
]