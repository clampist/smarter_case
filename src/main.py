"""
Main entry point for the Smarter Case system.
Provides both CLI and programmatic interfaces for test case selection workflow.
"""
import asyncio
import argparse
import json
import sys
from typing import Dict, Any
from datetime import datetime

from .coordination.workflow_orchestrator import execute_workflow
from .utils.logger import get_logger


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Smarter Case - Intelligent Test Case Selection for CI/CD"
    )
    
    parser.add_argument(
        "--commit-hash",
        required=True,
        help="Git commit hash to analyze"
    )
    
    parser.add_argument(
        "--branch",
        default="main",
        help="Git branch name (default: main)"
    )
    
    parser.add_argument(
        "--time-range",
        default="24h",
        help="Time range for requirement analysis (default: 24h)"
    )
    
    parser.add_argument(
        "--project-key",
        default="PROJ",
        help="Jira project key (default: PROJ)"
    )
    
    parser.add_argument(
        "--output-format",
        choices=["json", "pretty"],
        default="pretty",
        help="Output format (default: pretty)"
    )
    
    parser.add_argument(
        "--output-file",
        help="Output file path (optional)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    logger = get_logger("main")
    if args.verbose:
        logger.setLevel("DEBUG")
    
    logger.info(f"Starting Smarter Case workflow for commit {args.commit_hash}")
    
    try:
        # Execute the workflow
        result = asyncio.run(execute_workflow(
            commit_hash=args.commit_hash,
            branch=args.branch,
            time_range=args.time_range,
            project_key=args.project_key
        ))
        
        # Format output
        if args.output_format == "json":
            output = json.dumps(result, indent=2)
        else:
            output = format_pretty_output(result)
        
        # Output results
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(output)
            logger.info(f"Results written to {args.output_file}")
        else:
            print(output)
        
        # Exit with appropriate code
        sys.exit(0 if result.get("status") == "completed" else 1)
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        print(f"Error: {e}")
        sys.exit(1)


def format_pretty_output(result: Dict[str, Any]) -> str:
    """Format the result in a human-readable format."""
    output = []
    
    # Header
    output.append("=" * 60)
    output.append("🧪 SMARTER CASE - TEST SELECTION RESULTS")
    output.append("=" * 60)
    
    # Basic info
    output.append(f"Workflow ID: {result.get('workflow_id', 'N/A')}")
    output.append(f"Commit Hash: {result.get('commit_hash', 'N/A')}")
    output.append(f"Branch: {result.get('branch', 'N/A')}")
    output.append(f"Status: {result.get('status', 'N/A')}")
    output.append(f"Timestamp: {result.get('timestamp', 'N/A')}")
    output.append("")
    
    # Plan steps
    if 'plan_steps' in result:
        output.append("📋 EXECUTION PLAN:")
        output.append("-" * 40)
        for i, step in enumerate(result['plan_steps'], 1):
            output.append(f"{i}. {step}")
        output.append("")
    
    # Results
    if 'results' in result:
        output.append("📊 EXECUTION RESULTS:")
        output.append("-" * 40)
        for step_key, step_result in result['results'].items():
            output.append(f"\n{step_key.upper()}:")
            output.append(f"  Agent: {step_result.get('agent', 'N/A')}")
            output.append(f"  Title: {step_result.get('title', 'N/A')}")
            output.append(f"  Status: {step_result.get('timestamp', 'N/A')}")
            
            # Truncate long outputs
            output_text = step_result.get('output', '')
            if len(output_text) > 500:
                output_text = output_text[:500] + "... (truncated)"
            output.append(f"  Output: {output_text}")
    
    # Error handling
    if 'error' in result:
        output.append("\n❌ ERROR:")
        output.append("-" * 40)
        output.append(result['error'])
    
    output.append("\n" + "=" * 60)
    
    return "\n".join(output)


async def run_workflow_async(
    commit_hash: str,
    branch: str = "main",
    time_range: str = "24h",
    project_key: str = "PROJ"
) -> Dict[str, Any]:
    """
    Programmatic interface for running the workflow.
    
    Args:
        commit_hash: Git commit hash to analyze
        branch: Git branch name
        time_range: Time range for requirement analysis
        project_key: Jira project key
        
    Returns:
        Dict containing workflow results
    """
    return await execute_workflow(commit_hash, branch, time_range, project_key)


if __name__ == "__main__":
    main()
