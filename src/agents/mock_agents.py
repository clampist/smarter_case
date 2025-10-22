"""
Mock Agent implementations for testing and development.
"""
from typing import Dict, Any
import json
from datetime import datetime


def mock_llm_call(prompt: str, agent_name: str) -> str:
    """
    Mock LLM call function that returns predefined responses based on agent name.
    This allows testing the system architecture without requiring live API keys.
    """
    mock_responses = {
        "code_analysis_agent": json.dumps({
            "commit_hash": "abc123def456",
            "branch": "main",
            "files_changed": [
                "src/api/user_service.py",
                "src/models/user.py", 
                "tests/test_user_service.py"
            ],
            "change_categories": {
                "api": ["src/api/user_service.py"],
                "models": ["src/models/user.py"],
                "tests": ["tests/test_user_service.py"]
            },
            "impact_modules": ["user_management", "authentication"],
            "business_domains": ["user_management", "authentication"],
            "risk_level": "medium",
            "test_priorities": {
                "critical": ["user_service_api_tests", "user_model_tests"],
                "important": ["authentication_tests"],
                "optional": ["integration_tests"]
            },
            "confidence_score": 0.85
        }),
        
        "requirement_analysis_agent": json.dumps({
            "time_range": "24h",
            "project_key": "PROJ",
            "requirement_changes": [
                {
                    "id": "REQ-123",
                    "title": "User Profile Enhancement",
                    "type": "new",
                    "priority": "high",
                    "business_domain": "user_management",
                    "description": "Add new user profile features"
                }
            ],
            "business_domains_affected": ["user_management"],
            "priority_requirements": {
                "critical": [],
                "high": ["REQ-123"],
                "medium": [],
                "low": []
            },
            "test_impact": {
                "api_tests": ["user_profile_api"],
                "ui_tests": ["user_profile_ui"],
                "integration_tests": ["user_management_flow"]
            },
            "risk_assessment": "medium",
            "confidence_score": 0.80
        }),
        
        "test_selection_agent": json.dumps({
            "selected_tests": {
                "api_tests": [
                    {
                        "test_id": "test_user_service_001",
                        "test_name": "Test User Service API",
                        "priority": "critical",
                        "reason": "Core user management functionality",
                        "estimated_time": "5 minutes",
                        "framework": "pytest"
                    }
                ],
                "ui_tests": [
                    {
                        "test_id": "test_user_profile_001", 
                        "test_name": "Test User Profile Page",
                        "priority": "high",
                        "reason": "New user profile features",
                        "estimated_time": "3 minutes",
                        "framework": "playwright"
                    }
                ]
            },
            "selection_summary": {
                "total_tests_selected": 2,
                "estimated_execution_time": "8 minutes",
                "coverage_areas": ["user_management", "authentication"],
                "risk_level": "medium"
            },
            "rationale": "Selected tests focus on core user management changes and new profile features",
            "confidence_score": 0.88
        }),
        
        "reflection_agent": json.dumps({
            "reflection_analysis": {
                "strengths": ["Good coverage of critical paths", "Reasonable test selection"],
                "weaknesses": ["Could include more edge cases"],
                "risks": ["Authentication edge cases not fully covered"],
                "optimization_opportunities": ["Add more boundary tests", "Include negative test cases"]
            },
            "optimized_selection": {
                "api_tests": [
                    {
                        "test_id": "test_user_service_001",
                        "test_name": "Test User Service API",
                        "priority": "critical",
                        "reason": "Core user management functionality",
                        "estimated_time": "5 minutes",
                        "framework": "pytest",
                        "optimization_note": "Enhanced with edge cases"
                    },
                    {
                        "test_id": "test_auth_edge_cases",
                        "test_name": "Test Authentication Edge Cases",
                        "priority": "high",
                        "reason": "Cover authentication edge cases",
                        "estimated_time": "3 minutes",
                        "framework": "pytest",
                        "optimization_note": "Added for better coverage"
                    }
                ],
                "ui_tests": [
                    {
                        "test_id": "test_user_profile_001",
                        "test_name": "Test User Profile Page", 
                        "priority": "high",
                        "reason": "New user profile features",
                        "estimated_time": "3 minutes",
                        "framework": "playwright",
                        "optimization_note": "Original selection maintained"
                    }
                ]
            },
            "optimization_summary": {
                "changes_made": ["Added authentication edge case tests"],
                "improvement_areas": ["Better authentication coverage"],
                "time_saved": "0 minutes",
                "coverage_improved": True
            },
            "final_recommendation": "Enhanced selection provides better coverage while maintaining efficiency",
            "confidence_score": 0.92
        }),
        
        "execution_agent": json.dumps({
            "platform": "github-actions",
            "execution_commands": {
                "setup": [
                    "pip install -r requirements.txt",
                    "pip install pytest playwright",
                    "playwright install"
                ],
                "api_tests": [
                    "pytest tests/api/ -v --tb=short --maxfail=5"
                ],
                "ui_tests": [
                    "pytest tests/ui/ -v --tb=short --maxfail=3"
                ],
                "cleanup": [
                    "rm -rf test-results/",
                    "rm -rf coverage/"
                ]
            },
            "parallel_execution": {
                "enabled": True,
                "strategy": "Run API and UI tests in parallel",
                "max_parallel_jobs": 2
            },
            "environment_variables": {
                "TEST_ENV": "ci",
                "LOG_LEVEL": "INFO",
                "HEADLESS": "true"
            },
            "execution_summary": {
                "total_commands": 6,
                "estimated_execution_time": "8 minutes",
                "parallel_efficiency": "75%"
            },
            "configuration_files": {
                "pytest_ini": "[tool:pytest]\ntestpaths = tests\npython_files = test_*.py\npython_classes = Test*\npython_functions = test_*",
                "playwright_config": "import { defineConfig } from '@playwright/test';\nexport default defineConfig({\n  testDir: './tests/ui',\n  timeout: 30000,\n  retries: 1\n});"
            }
        })
    }
    
    return mock_responses.get(agent_name, f"Mock response for {agent_name}: {prompt[:100]}...")


def get_mock_agent_response(agent_name: str) -> Dict[str, Any]:
    """
    Get a mock response for a specific agent.
    """
    mock_data = {
        "code_analysis_agent": {
            "agent": "code_analysis_agent",
            "timestamp": datetime.now().isoformat(),
            "input": {"commit_hash": "abc123def456", "branch": "main"},
            "output": mock_llm_call("", "code_analysis_agent"),
            "status": "completed"
        },
        "requirement_analysis_agent": {
            "agent": "requirement_analysis_agent", 
            "timestamp": datetime.now().isoformat(),
            "input": {"time_range": "24h", "project_key": "PROJ"},
            "output": mock_llm_call("", "requirement_analysis_agent"),
            "status": "completed"
        },
        "test_selection_agent": {
            "agent": "test_selection_agent",
            "timestamp": datetime.now().isoformat(),
            "input": {"code_analysis": {}, "requirement_analysis": {}},
            "output": mock_llm_call("", "test_selection_agent"),
            "status": "completed"
        },
        "reflection_agent": {
            "agent": "reflection_agent",
            "timestamp": datetime.now().isoformat(),
            "input": {"test_selection": {}},
            "output": mock_llm_call("", "reflection_agent"),
            "status": "completed"
        },
        "execution_agent": {
            "agent": "execution_agent",
            "timestamp": datetime.now().isoformat(),
            "input": {"optimized_selection": {}, "ci_cd_platform": "github-actions"},
            "output": mock_llm_call("", "execution_agent"),
            "status": "completed"
        }
    }
    
    return mock_data.get(agent_name, {})
