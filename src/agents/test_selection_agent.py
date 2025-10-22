"""
Test Selection Agent - intelligently selects test cases based on analysis results.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import aisuite as ai

from ..utils.logger import get_logger
from ..config.agent_config import AgentConfig


# Initialize AI client
client = ai.Client()


def test_selection_agent(
    code_analysis: Dict[str, Any],
    requirement_analysis: Dict[str, Any],
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Test Selection Agent - intelligently selects test cases based on analysis results.
    
    Args:
        code_analysis: Results from code analysis agent
        requirement_analysis: Results from requirement analysis agent
        model: AI model to use for selection (optional, uses config default)
        
    Returns:
        Dict containing test selection results
    """
    print("==================================")
    print("🧪 Test Selection Agent")
    print("==================================")
    
    # Get configuration for this agent
    agent_config = AgentConfig.get_agent_config("test_selection")
    model = model or agent_config["model"]
    temperature = agent_config["temperature"]
    max_tokens = agent_config["max_tokens"]
    
    prompt = f"""
You are a test selection expert responsible for intelligently selecting test cases based on code changes and requirement analysis.

## Your Task:
Based on the provided analysis results, select the most relevant test cases to execute.

## Input Analysis:
**Code Analysis Results:**
{code_analysis.get('output', 'No code analysis available')}

**Requirement Analysis Results:**
{requirement_analysis.get('output', 'No requirement analysis available')}

## Selection Criteria:
1. **Impact-Based Selection**: Prioritize tests for areas with the highest impact
2. **Risk-Based Selection**: Include tests for high-risk changes
3. **Coverage Optimization**: Ensure adequate coverage while minimizing execution time
4. **Framework Consideration**: Consider both API tests (Pytest) and UI tests (Playwright)
5. **Priority Balancing**: Balance between critical path tests and regression tests

## Output Format:
Provide your test selection in the following JSON structure:
{{
    "selected_tests": {{
        "api_tests": [
            {{
                "test_id": "test_001",
                "test_name": "Test name",
                "priority": "critical|high|medium|low",
                "reason": "reason for selection",
                "estimated_time": "time in minutes",
                "framework": "pytest"
            }}
        ],
        "ui_tests": [
            {{
                "test_id": "test_002",
                "test_name": "Test name",
                "priority": "critical|high|medium|low",
                "reason": "reason for selection",
                "estimated_time": "time in minutes",
                "framework": "playwright"
            }}
        ]
    }},
    "selection_summary": {{
        "total_tests_selected": 0,
        "estimated_execution_time": "total time in minutes",
        "coverage_areas": ["list of covered areas"],
        "risk_level": "low|medium|high"
    }},
    "rationale": "explanation of selection decisions",
    "confidence_score": 0.0-1.0
}}

Focus on selecting the most effective test cases that will catch the most critical issues.
"""
    
    try:
        # Check if we should use mock or real AI
        if model == "mock":
            from .mock_agents import mock_llm_call
            content = mock_llm_call(prompt, "test_selection_agent")
        else:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content or ""
        
        print("✅ Test Selection Output:")
        print(content)
        
        return {
            "agent": "test_selection_agent",
            "timestamp": datetime.now().isoformat(),
            "input": {
                "code_analysis": code_analysis,
                "requirement_analysis": requirement_analysis
            },
            "output": content,
            "status": "completed"
        }
        
    except Exception as e:
        print(f"❌ Test Selection Error: {e}")
        return {
            "agent": "test_selection_agent",
            "timestamp": datetime.now().isoformat(),
            "input": {
                "code_analysis": code_analysis,
                "requirement_analysis": requirement_analysis
            },
            "output": f"Error: {str(e)}",
            "status": "failed"
        }
