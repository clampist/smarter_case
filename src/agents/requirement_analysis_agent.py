"""
Requirement Analysis Agent - analyzes requirement changes from Jira.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import json
import aisuite as ai

from ..utils.logger import get_logger
from ..config.agent_config import AgentConfig
from ..tools.jira_tools import JiraTools


# Initialize AI client
client = ai.Client()


async def requirement_analysis_agent(
    time_range: str = "24h",
    project_key: str = "PROJ",
    model: Optional[str] = None,
    use_jira: bool = False,
    jira_config: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Requirement Analysis Agent - analyzes requirement changes from Jira.
    
    Args:
        time_range: Time range to analyze (e.g., "24h", "7d", "1w")
        project_key: Jira project key
        model: AI model to use for analysis (optional, uses config default)
        use_jira: Whether to use real Jira API or mock data
        jira_config: Jira configuration (url, username, api_token)
        
    Returns:
        Dict containing requirement analysis results
    """
    print("==================================")
    print("📋 Requirement Analysis Agent")
    print("==================================")
    
    # Get configuration for this agent
    agent_config = AgentConfig.get_agent_config("requirement_analysis")
    model = model or agent_config["model"]
    temperature = agent_config["temperature"]
    max_tokens = agent_config["max_tokens"]
    
    prompt = f"""
You are a requirements analysis expert responsible for analyzing requirement changes and their business impact.

## Your Task:
Analyze requirement changes in the last {time_range} for project {project_key} and assess their impact on testing priorities.

## Analysis Requirements:
1. **Requirement Changes**: Identify new, modified, or completed requirements
2. **Business Impact**: Assess the business domains affected by these changes
3. **Priority Assessment**: Determine the priority level of each requirement
4. **Test Impact**: Identify which test areas should be prioritized based on requirements
5. **Risk Assessment**: Evaluate potential risks from requirement changes

## Output Format:
Provide your analysis in the following JSON structure:
{{
    "time_range": "{time_range}",
    "project_key": "{project_key}",
    "requirement_changes": [
        {{
            "id": "REQ-123",
            "title": "Requirement title",
            "type": "new|modified|completed",
            "priority": "low|medium|high|critical",
            "business_domain": "domain name",
            "description": "brief description"
        }}
    ],
    "business_domains_affected": ["list of affected domains"],
    "priority_requirements": {{
        "critical": ["list of critical requirements"],
        "high": ["list of high priority requirements"],
        "medium": ["list of medium priority requirements"],
        "low": ["list of low priority requirements"]
    }},
    "test_impact": {{
        "api_tests": ["areas needing API test focus"],
        "ui_tests": ["areas needing UI test focus"],
        "integration_tests": ["areas needing integration test focus"]
    }},
    "risk_assessment": "low|medium|high",
    "confidence_score": 0.0-1.0
}}

Focus on providing actionable insights for test case selection based on requirement changes.
"""
    
    try:
        # Get requirement data from Jira if enabled
        jira_data = None
        if use_jira and jira_config:
            try:
                jira_tools = JiraTools(
                    jira_url=jira_config.get('url', ''),
                    username=jira_config.get('username', ''),
                    api_token=jira_config.get('api_token', '')
                )
                
                # Test connection first
                if await jira_tools.test_connection():
                    jira_data = await jira_tools.get_requirement_changes(
                        project_key=project_key,
                        time_range=time_range
                    )
                    print("✅ Successfully fetched data from Jira API")
                else:
                    print("⚠️ Failed to connect to Jira API, using mock data")
                    
            except Exception as e:
                print(f"⚠️ Jira API error: {e}, using mock data")
        
        # If we have Jira data, include it in the prompt
        if jira_data:
            prompt += f"\n\n## Actual Jira Data:\n{json.dumps(jira_data, indent=2)}"
        
        # Check if we should use mock or real AI
        if model == "mock":
            from .mock_agents import mock_llm_call
            content = mock_llm_call(prompt, "requirement_analysis_agent")
        else:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content or ""
        
        print("✅ Requirement Analysis Output:")
        print(content)
        
        return {
            "agent": "requirement_analysis_agent",
            "timestamp": datetime.now().isoformat(),
            "input": {"time_range": time_range, "project_key": project_key},
            "output": content,
            "status": "completed"
        }
        
    except Exception as e:
        print(f"❌ Requirement Analysis Error: {e}")
        return {
            "agent": "requirement_analysis_agent",
            "timestamp": datetime.now().isoformat(),
            "input": {"time_range": time_range, "project_key": project_key},
            "output": f"Error: {str(e)}",
            "status": "failed"
        }


def requirement_analysis_agent_sync(
    time_range: str = "24h",
    project_key: str = "PROJ",
    model: Optional[str] = None,
    use_jira: bool = False,
    jira_config: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Synchronous wrapper for requirement analysis agent.
    
    Args:
        time_range: Time range to analyze (e.g., "24h", "7d", "1w")
        project_key: Jira project key
        model: AI model to use for analysis (optional, uses config default)
        use_jira: Whether to use real Jira API or mock data
        jira_config: Jira configuration (url, username, api_token)
        
    Returns:
        Dict containing requirement analysis results
    """
    import asyncio
    
    # Run the async function in the event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, we need to use a different approach
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    requirement_analysis_agent(time_range, project_key, model, use_jira, jira_config)
                )
                return future.result()
        else:
            return loop.run_until_complete(
                requirement_analysis_agent(time_range, project_key, model, use_jira, jira_config)
            )
    except RuntimeError:
        # No event loop exists, create a new one
        return asyncio.run(
            requirement_analysis_agent(time_range, project_key, model, use_jira, jira_config)
        )
