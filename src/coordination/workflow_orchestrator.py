"""
Workflow Orchestrator for coordinating the Smarter Case agent workflow.
Follows the agentic-ai pattern with planning and execution phases.
"""
import json
import asyncio
from typing import List, Dict, Any, Tuple
from datetime import datetime

import aisuite as ai
from ..agents.simple_agents import (
    code_analysis_agent,
    requirement_analysis_agent,
    test_selection_agent,
    reflection_agent,
    execution_agent
)
from ..utils.logger import get_logger

# Initialize AI client
client = ai.Client()


def planner_agent(
    commit_hash: str, 
    branch: str = "main",
    time_range: str = "24h",
    project_key: str = "PROJ",
    model: str = "openai:gpt-4o"
) -> List[str]:
    """
    Planning Agent - creates a step-by-step plan for the test selection workflow.
    
    Args:
        commit_hash: Git commit hash to analyze
        branch: Git branch name
        time_range: Time range for requirement analysis
        project_key: Jira project key
        model: AI model to use for planning
        
    Returns:
        List of step descriptions for the workflow
    """
    prompt = f"""
You are a planning agent responsible for organizing a test selection workflow using multiple intelligent agents.

🧠 Available agents:
- Code Analysis Agent: Analyzes Git commits to identify changed files and impact scope
- Requirement Analysis Agent: Analyzes requirement changes from Jira to understand business impact
- Test Selection Agent: Intelligently selects test cases based on code and requirement analysis
- Reflection Agent: Critically analyzes and optimizes the test selection using reflection design pattern
- Execution Agent: Generates CI/CD execution commands for different environments

🎯 Produce a clear step-by-step workflow plan **as a valid Python list of strings** (no markdown, no explanations).
Each step must be atomic, actionable, and assigned to one of the agents.
Maximum of 6 steps.

🚫 DO NOT include steps like "create CSV", "set up repo", "install packages".
✅ Focus on meaningful test selection tasks (analyze, select, optimize, execute).
✅ The FIRST step MUST be exactly:
"Code Analysis Agent: Analyze commit {commit_hash} on branch {branch} to identify changed files and impact scope."
✅ The SECOND step MUST be exactly:
"Requirement Analysis Agent: Analyze requirement changes in the last {time_range} for project {project_key} to understand business impact."
✅ The THIRD step MUST be exactly:
"Test Selection Agent: Select optimal test cases based on code analysis and requirement analysis results."
✅ The FOURTH step MUST be exactly:
"Reflection Agent: Critically analyze and optimize the test selection using reflection design pattern."
✅ The FIFTH step MUST be exactly:
"Execution Agent: Generate CI/CD execution commands for GitHub Actions and Jenkins environments."

🔚 The workflow should focus on:
- Analyzing code changes and requirement changes
- Intelligently selecting test cases
- Optimizing the selection through reflection
- Generating execution commands for CI/CD

Commit: {commit_hash}
Branch: {branch}
Time Range: {time_range}
Project: {project_key}
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )

        raw = response.choices[0].message.content.strip()

        # Parse the response to extract steps
        def _extract_steps(s: str) -> List[str]:
            # Try to find list-like structure
            lines = s.split('\n')
            steps = []
            
            for line in lines:
                line = line.strip()
                # Look for numbered steps or bullet points
                if (line.startswith('1.') or line.startswith('-') or 
                    line.startswith('*') or 'Agent:' in line):
                    # Clean up the line
                    step = line
                    if step.startswith('1.') or step.startswith('-') or step.startswith('*'):
                        step = step[2:].strip()
                    steps.append(step)
            
            return steps[:6]  # Limit to 6 steps

        steps = _extract_steps(raw)

        # Ensure we have the required steps
        required_steps = [
            f"Code Analysis Agent: Analyze commit {commit_hash} on branch {branch} to identify changed files and impact scope.",
            f"Requirement Analysis Agent: Analyze requirement changes in the last {time_range} for project {project_key} to understand business impact.",
            "Test Selection Agent: Select optimal test cases based on code analysis and requirement analysis results.",
            "Reflection Agent: Critically analyze and optimize the test selection using reflection design pattern.",
            "Execution Agent: Generate CI/CD execution commands for GitHub Actions and Jenkins environments."
        ]

        # Use required steps if parsing failed or steps are insufficient
        if len(steps) < 3:
            steps = required_steps

        return steps[:6]  # Ensure max 6 steps

    except Exception as e:
        # Fallback to required steps if planning fails
        return [
            f"Code Analysis Agent: Analyze commit {commit_hash} on branch {branch} to identify changed files and impact scope.",
            f"Requirement Analysis Agent: Analyze requirement changes in the last {time_range} for project {project_key} to understand business impact.",
            "Test Selection Agent: Select optimal test cases based on code analysis and requirement analysis results.",
            "Reflection Agent: Critically analyze and optimize the test selection using reflection design pattern.",
            "Execution Agent: Generate CI/CD execution commands for GitHub Actions and Jenkins environments."
        ]


def executor_agent_step(
    step_title: str, 
    history: List[Tuple[str, str, str]], 
    commit_hash: str,
    branch: str = "main",
    time_range: str = "24h",
    project_key: str = "PROJ"
) -> Tuple[str, str, str]:
    """
    Executes a step of the executor agent.
    
    Args:
        step_title: Title of the step to execute
        history: Execution history so far
        commit_hash: Git commit hash
        branch: Git branch name
        time_range: Time range for requirement analysis
        project_key: Jira project key
        
    Returns:
        Tuple of (step_title, agent_name, output)
    """
    
    # Build enriched context from history
    context = f"📘 Workflow Context:\nCommit: {commit_hash}\nBranch: {branch}\nTime Range: {time_range}\nProject: {project_key}\n\n📜 History so far:\n"
    
    for i, (desc, agent, output) in enumerate(history):
        if "code analysis" in desc.lower() or agent == "code_analysis_agent":
            context += f"\n🔍 Code Analysis (Step {i + 1}):\n{output.strip()}\n"
        elif "requirement analysis" in desc.lower() or agent == "requirement_analysis_agent":
            context += f"\n📋 Requirement Analysis (Step {i + 1}):\n{output.strip()}\n"
        elif "test selection" in desc.lower() or agent == "test_selection_agent":
            context += f"\n🧪 Test Selection (Step {i + 1}):\n{output.strip()}\n"
        elif "reflection" in desc.lower() or agent == "reflection_agent":
            context += f"\n🔄 Reflection (Step {i + 1}):\n{output.strip()}\n"
        elif "execution" in desc.lower() or agent == "execution_agent":
            context += f"\n⚡ Execution (Step {i + 1}):\n{output.strip()}\n"
        else:
            context += f"\n🧩 Other (Step {i + 1}) by {agent}:\n{output.strip()}\n"

    # Select agent based on step content
    step_lower = step_title.lower()
    
    if "code analysis" in step_lower:
        result = code_analysis_agent(commit_hash, branch)
        return step_title, "code_analysis_agent", result.get('output', '')
    
    elif "requirement analysis" in step_lower:
        result = requirement_analysis_agent(time_range, project_key)
        return step_title, "requirement_analysis_agent", result.get('output', '')
    
    elif "test selection" in step_lower:
        # Get results from previous steps
        code_analysis = None
        requirement_analysis = None
        
        for desc, agent, output in history:
            if agent == "code_analysis_agent":
                code_analysis = {"output": output}
            elif agent == "requirement_analysis_agent":
                requirement_analysis = {"output": output}
        
        if code_analysis and requirement_analysis:
            result = test_selection_agent(code_analysis, requirement_analysis)
            return step_title, "test_selection_agent", result.get('output', '')
        else:
            error_msg = "Missing code analysis or requirement analysis results for test selection"
            return step_title, "test_selection_agent", f"Error: {error_msg}"
    
    elif "reflection" in step_lower:
        # Get test selection result
        test_selection = None
        for desc, agent, output in history:
            if agent == "test_selection_agent":
                test_selection = {"output": output}
        
        if test_selection:
            result = reflection_agent(test_selection)
            return step_title, "reflection_agent", result.get('output', '')
        else:
            error_msg = "Missing test selection results for reflection"
            return step_title, "reflection_agent", f"Error: {error_msg}"
    
    elif "execution" in step_lower:
        # Get reflection result
        reflection_result = None
        for desc, agent, output in history:
            if agent == "reflection_agent":
                reflection_result = {"output": output}
        
        if reflection_result:
            # Generate commands for both platforms
            github_result = execution_agent(reflection_result, "github-actions")
            jenkins_result = execution_agent(reflection_result, "jenkins")
            
            combined_output = f"GitHub Actions Commands:\n{github_result.get('output', '')}\n\nJenkins Commands:\n{jenkins_result.get('output', '')}"
            return step_title, "execution_agent", combined_output
        else:
            error_msg = "Missing reflection results for execution"
            return step_title, "execution_agent", f"Error: {error_msg}"
    
    else:
        raise ValueError(f"Unknown step type: {step_title}")


async def execute_workflow(
    commit_hash: str,
    branch: str = "main",
    time_range: str = "24h",
    project_key: str = "PROJ"
) -> Dict[str, Any]:
    """
    Execute the complete test selection workflow.
    
    Args:
        commit_hash: Git commit hash to analyze
        branch: Git branch name
        time_range: Time range for requirement analysis
        project_key: Jira project key
        
    Returns:
        Dict containing workflow results
    """
    logger = get_logger("workflow_orchestrator")
    
    logger.info(f"Starting workflow for commit {commit_hash} on branch {branch}")
    
    try:
        # Step 1: Create execution plan
        plan_steps = planner_agent(commit_hash, branch, time_range, project_key)
        logger.info(f"Created execution plan with {len(plan_steps)} steps")
        
        # Step 2: Execute the workflow
        execution_history = []
        results = {}
        
        for i, step_title in enumerate(plan_steps):
            logger.info(f"Executing step {i + 1}: {step_title}")
            
            step_desc, agent_name, output = executor_agent_step(
                step_title, 
                execution_history, 
                commit_hash, 
                branch, 
                time_range, 
                project_key
            )
            
            execution_history.append((step_desc, agent_name, output))
            results[f"step_{i + 1}"] = {
                "title": step_desc,
                "agent": agent_name,
                "output": output,
                "timestamp": datetime.now().isoformat()
            }
        
        # Step 3: Compile final results
        final_result = {
            "workflow_id": f"workflow_{commit_hash}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "commit_hash": commit_hash,
            "branch": branch,
            "time_range": time_range,
            "project_key": project_key,
            "plan_steps": plan_steps,
            "execution_history": execution_history,
            "results": results,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("Workflow completed successfully")
        return final_result
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        return {
            "workflow_id": f"workflow_{commit_hash}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "commit_hash": commit_hash,
            "branch": branch,
            "time_range": time_range,
            "project_key": project_key,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
