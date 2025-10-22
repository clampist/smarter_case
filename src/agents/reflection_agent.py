"""
Reflection Agent - reflects on and optimizes test selection using reflection design pattern.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import aisuite as ai

from ..utils.logger import get_logger
from ..config.agent_config import AgentConfig


# Initialize AI client
client = ai.Client()


def reflection_agent(
    test_selection: Dict[str, Any],
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Reflection Agent - reflects on and optimizes test selection using reflection design pattern.
    
    Args:
        test_selection: Results from test selection agent
        model: AI model to use for reflection (optional, uses config default)
        
    Returns:
        Dict containing reflection and optimization results
    """
    print("==================================")
    print("🔄 Reflection Agent")
    print("==================================")
    
    # Get configuration for this agent
    agent_config = AgentConfig.get_agent_config("reflection")
    model = model or agent_config["model"]
    temperature = agent_config["temperature"]
    max_tokens = agent_config["max_tokens"]
    
    prompt = f"""
You are a reflection expert responsible for critically analyzing and optimizing test selection decisions.

## Your Task:
Critically analyze the test selection and provide optimized recommendations.

## Input Test Selection:
{test_selection.get('output', 'No test selection available')}

## Reflection Process:
1. **Critical Analysis**: Identify potential gaps or issues in the current selection
2. **Optimization Opportunities**: Find ways to improve the selection
3. **Risk Assessment**: Evaluate if the selection adequately covers risks
4. **Efficiency Review**: Check if the selection is optimal for time and resources
5. **Coverage Analysis**: Ensure comprehensive coverage of critical areas

## Output Format:
Provide your reflection and optimization in the following JSON structure:
{{
    "reflection_analysis": {{
        "strengths": ["list of strengths in current selection"],
        "weaknesses": ["list of weaknesses or gaps"],
        "risks": ["list of potential risks not covered"],
        "optimization_opportunities": ["list of optimization opportunities"]
    }},
    "optimized_selection": {{
        "api_tests": [
            {{
                "test_id": "test_001",
                "test_name": "Test name",
                "priority": "critical|high|medium|low",
                "reason": "reason for selection",
                "estimated_time": "time in minutes",
                "framework": "pytest",
                "optimization_note": "note about optimization"
            }}
        ],
        "ui_tests": [
            {{
                "test_id": "test_002",
                "test_name": "Test name",
                "priority": "critical|high|medium|low",
                "reason": "reason for selection",
                "estimated_time": "time in minutes",
                "framework": "playwright",
                "optimization_note": "note about optimization"
            }}
        ]
    }},
    "optimization_summary": {{
        "changes_made": ["list of changes made"],
        "improvement_areas": ["list of areas improved"],
        "time_saved": "time saved in minutes",
        "coverage_improved": true/false
    }},
    "final_recommendation": "final recommendation and rationale",
    "confidence_score": 0.0-1.0
}}

Focus on providing actionable improvements to the test selection.
"""
    
    try:
        # Check if we should use mock or real AI
        if model == "mock":
            from .mock_agents import mock_llm_call
            content = mock_llm_call(prompt, "reflection_agent")
        else:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content or ""
        
        print("✅ Reflection Output:")
        print(content)
        
        return {
            "agent": "reflection_agent",
            "timestamp": datetime.now().isoformat(),
            "input": {"test_selection": test_selection},
            "output": content,
            "status": "completed"
        }
        
    except Exception as e:
        print(f"❌ Reflection Error: {e}")
        return {
            "agent": "reflection_agent",
            "timestamp": datetime.now().isoformat(),
            "input": {"test_selection": test_selection},
            "output": f"Error: {str(e)}",
            "status": "failed"
        }
