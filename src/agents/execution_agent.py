"""
Execution Agent - generates CI/CD execution commands for different environments.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import aisuite as ai

from ..utils.logger import get_logger
from ..config.agent_config import AgentConfig


# Initialize AI client
client = ai.Client()


def execution_agent(
    optimized_selection: Dict[str, Any],
    ci_cd_platform: str = "github-actions",
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execution Agent - generates CI/CD execution commands for different environments.
    
    Args:
        optimized_selection: Results from reflection agent
        ci_cd_platform: CI/CD platform (github-actions, jenkins)
        model: AI model to use for command generation (optional, uses config default)
        
    Returns:
        Dict containing execution commands and configuration
    """
    print("==================================")
    print("⚡ Execution Agent")
    print("==================================")
    
    # Get configuration for this agent
    agent_config = AgentConfig.get_agent_config("execution")
    model = model or agent_config["model"]
    temperature = agent_config["temperature"]
    max_tokens = agent_config["max_tokens"]
    
    prompt = f"""
You are an execution expert responsible for generating CI/CD execution commands for test automation.

## Your Task:
Generate execution commands for the optimized test selection on {ci_cd_platform}.

## Input Optimized Selection:
{optimized_selection.get('output', 'No optimized selection available')}

## Execution Requirements:
1. **Platform-Specific Commands**: Generate commands specific to {ci_cd_platform}
2. **Test Framework Commands**: Include both Pytest and Playwright execution commands
3. **Parallel Execution**: Optimize for parallel execution where possible
4. **Environment Configuration**: Include necessary environment setup
5. **Error Handling**: Include proper error handling and reporting

## Output Format:
Provide your execution commands in the following JSON structure:
{{
    "platform": "{ci_cd_platform}",
    "execution_commands": {{
        "setup": [
            "command to setup environment",
            "command to install dependencies"
        ],
        "api_tests": [
            "pytest command for API tests"
        ],
        "ui_tests": [
            "playwright command for UI tests"
        ],
        "cleanup": [
            "command to cleanup after execution"
        ]
    }},
    "parallel_execution": {{
        "enabled": true/false,
        "strategy": "parallel strategy description",
        "max_parallel_jobs": 0
    }},
    "environment_variables": {{
        "variable_name": "variable_value"
    }},
    "execution_summary": {{
        "total_commands": 0,
        "estimated_execution_time": "total time in minutes",
        "parallel_efficiency": "efficiency percentage"
    }},
    "configuration_files": {{
        "pytest_ini": "pytest configuration content",
        "playwright_config": "playwright configuration content"
    }}
}}

Focus on providing executable commands that can be directly used in CI/CD pipelines.
"""
    
    try:
        # Check if we should use mock or real AI
        if model == "mock":
            from .mock_agents import mock_llm_call
            content = mock_llm_call(prompt, "execution_agent")
        else:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content or ""
        
        print("✅ Execution Output:")
        print(content)
        
        return {
            "agent": "execution_agent",
            "timestamp": datetime.now().isoformat(),
            "input": {
                "optimized_selection": optimized_selection,
                "ci_cd_platform": ci_cd_platform
            },
            "output": content,
            "status": "completed"
        }
        
    except Exception as e:
        print(f"❌ Execution Error: {e}")
        return {
            "agent": "execution_agent",
            "timestamp": datetime.now().isoformat(),
            "input": {
                "optimized_selection": optimized_selection,
                "ci_cd_platform": ci_cd_platform
            },
            "output": f"Error: {str(e)}",
            "status": "failed"
        }
