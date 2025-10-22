"""
Simple Agent implementations following the agentic-ai style.
These agents are designed to be lightweight and focused on specific tasks.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import aisuite as ai

from ..utils.logger import get_logger


# Initialize AI client
client = ai.Client()


def code_analysis_agent(
    commit_hash: str, 
    branch: str = "main",
    model: str = "openai:gpt-4o"
) -> Dict[str, Any]:
    """
    Code Analysis Agent - analyzes Git changes and identifies impact scope.
    
    Args:
        commit_hash: Git commit hash to analyze
        branch: Git branch name
        model: AI model to use for analysis
        
    Returns:
        Dict containing analysis results
    """
    print("==================================")
    print("🔍 Code Analysis Agent")
    print("==================================")
    
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
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # Low temperature for consistent analysis
            max_tokens=2000
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


def requirement_analysis_agent(
    time_range: str = "24h",
    project_key: str = "PROJ",
    model: str = "openai:gpt-4o"
) -> Dict[str, Any]:
    """
    Requirement Analysis Agent - analyzes requirement changes from Jira.
    
    Args:
        time_range: Time range to analyze (e.g., "24h", "7d", "1w")
        project_key: Jira project key
        model: AI model to use for analysis
        
    Returns:
        Dict containing requirement analysis results
    """
    print("==================================")
    print("📋 Requirement Analysis Agent")
    print("==================================")
    
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
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2000
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


def test_selection_agent(
    code_analysis: Dict[str, Any],
    requirement_analysis: Dict[str, Any],
    model: str = "openai:gpt-4o"
) -> Dict[str, Any]:
    """
    Test Selection Agent - intelligently selects test cases based on analysis results.
    
    Args:
        code_analysis: Results from code analysis agent
        requirement_analysis: Results from requirement analysis agent
        model: AI model to use for selection
        
    Returns:
        Dict containing test selection results
    """
    print("==================================")
    print("🧪 Test Selection Agent")
    print("==================================")
    
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
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=3000
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


def reflection_agent(
    test_selection: Dict[str, Any],
    model: str = "openai:gpt-4o"
) -> Dict[str, Any]:
    """
    Reflection Agent - reflects on and optimizes test selection using reflection design pattern.
    
    Args:
        test_selection: Results from test selection agent
        model: AI model to use for reflection
        
    Returns:
        Dict containing reflection and optimization results
    """
    print("==================================")
    print("🔄 Reflection Agent")
    print("==================================")
    
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
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=3000
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


def execution_agent(
    optimized_selection: Dict[str, Any],
    ci_cd_platform: str = "github-actions",
    model: str = "openai:gpt-4o"
) -> Dict[str, Any]:
    """
    Execution Agent - generates CI/CD execution commands for different environments.
    
    Args:
        optimized_selection: Results from reflection agent
        ci_cd_platform: CI/CD platform (github-actions, jenkins)
        model: AI model to use for command generation
        
    Returns:
        Dict containing execution commands and configuration
    """
    print("==================================")
    print("⚡ Execution Agent")
    print("==================================")
    
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
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=3000
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
