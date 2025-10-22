"""
Code Analysis Agent - analyzes Git changes and identifies impact scope.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import json
import aisuite as ai

from ..utils.logger import get_logger
from ..config.agent_config import AgentConfig
from ..tools.git_tools import GitAnalyzer


# Initialize AI client
client = ai.Client()


async def code_analysis_agent(
    commit_hash: str, 
    branch: str = "main",
    model: Optional[str] = None,
    use_git_analysis: bool = True
) -> Dict[str, Any]:
    """
    Code Analysis Agent - analyzes Git changes and identifies impact scope.
    
    Args:
        commit_hash: Git commit hash to analyze
        branch: Git branch name
        model: AI model to use for analysis (optional, uses config default)
        use_git_analysis: Whether to use enhanced Git analysis or mock data
        
    Returns:
        Dict containing analysis results
    """
    print("==================================")
    print("🔍 Code Analysis Agent")
    print("==================================")
    
    # Get configuration for this agent
    agent_config = AgentConfig.get_agent_config("code_analysis")
    model = model or agent_config["model"]
    temperature = agent_config["temperature"]
    max_tokens = agent_config["max_tokens"]
    
    prompt = f"""
You are a code analysis expert responsible for analyzing Git commits and identifying their impact scope.

## Your Task:
Analyze the commit {commit_hash} on branch {branch} and provide a comprehensive impact analysis.

## Analysis Requirements:
1. **Identify Changed Files**: List all files that were modified, added, or deleted
2. **Categorize Changes**: Classify changes by type (API, UI, Database, Configuration, Tests, etc.)
3. **Impact Assessment**: Determine which modules and business domains are affected
4. **Risk Evaluation**: Assess the potential impact on system functionality
5. **Test Recommendations**: Suggest which types of tests should be prioritized

## Output Format:
Provide your analysis in the following JSON structure:
{{
    "commit_hash": "{commit_hash}",
    "branch": "{branch}",
    "files_changed": ["list of file paths"],
    "change_categories": {{
        "api": ["affected API files"],
        "ui": ["affected UI files"],
        "database": ["affected database files"],
        "config": ["affected configuration files"],
        "tests": ["affected test files"]
    }},
    "impact_modules": ["list of affected modules"],
    "business_domains": ["list of affected business domains"],
    "risk_level": "low|medium|high",
    "test_priorities": {{
        "critical": ["high priority test areas"],
        "important": ["medium priority test areas"],
        "optional": ["low priority test areas"]
    }},
    "confidence_score": 0.0-1.0
}}

Focus on providing actionable insights for test case selection.
"""
    
    try:
        # Get Git analysis data if enabled
        git_analysis_data = None
        if use_git_analysis:
            try:
                git_analyzer = GitAnalyzer()
                
                # Get comprehensive commit analysis
                git_analysis_data = await git_analyzer.get_comprehensive_commit_analysis(commit_hash)
                
                # Get repository info
                repo_info = await git_analyzer.get_repository_info()
                
                # Combine Git analysis with repository info
                git_analysis_data['repository'] = {
                    'url': repo_info.url,
                    'current_branch': repo_info.current_branch,
                    'remotes': repo_info.remotes
                }
                
                print("✅ Successfully analyzed Git commit with enhanced tools")
                
            except Exception as e:
                print(f"⚠️ Git analysis error: {e}, using mock data")
                git_analysis_data = None
        
        # If we have Git analysis data, include it in the prompt
        if git_analysis_data:
            prompt += f"\n\n## Actual Git Analysis Data:\n{json.dumps(git_analysis_data, indent=2)}"
        
        # Check if we should use mock or real AI
        if model == "mock":
            from .mock_agents import mock_llm_call
            content = mock_llm_call(prompt, "code_analysis_agent")
        else:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content or ""
        
        print("✅ Code Analysis Output:")
        print(content)
        
        return {
            "agent": "code_analysis_agent",
            "timestamp": datetime.now().isoformat(),
            "input": {"commit_hash": commit_hash, "branch": branch},
            "output": content,
            "status": "completed"
        }
        
    except Exception as e:
        print(f"❌ Code Analysis Error: {e}")
        return {
            "agent": "code_analysis_agent",
            "timestamp": datetime.now().isoformat(),
            "input": {"commit_hash": commit_hash, "branch": branch},
            "output": f"Error: {str(e)}",
            "status": "failed"
        }


def code_analysis_agent_sync(
    commit_hash: str, 
    branch: str = "main",
    model: Optional[str] = None,
    use_git_analysis: bool = True
) -> Dict[str, Any]:
    """
    Synchronous wrapper for code analysis agent.
    
    Args:
        commit_hash: Git commit hash to analyze
        branch: Git branch name
        model: AI model to use for analysis (optional, uses config default)
        use_git_analysis: Whether to use enhanced Git analysis or mock data
        
    Returns:
        Dict containing analysis results
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
                    code_analysis_agent(commit_hash, branch, model, use_git_analysis)
                )
                return future.result()
        else:
            return loop.run_until_complete(
                code_analysis_agent(commit_hash, branch, model, use_git_analysis)
            )
    except RuntimeError:
        # No event loop exists, create a new one
        return asyncio.run(
            code_analysis_agent(commit_hash, branch, model, use_git_analysis)
        )