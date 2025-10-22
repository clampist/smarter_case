"""
Basic usage example for the Smarter Case system.
Demonstrates how to use the agentic workflow for test case selection.
"""
import asyncio
import json
from src.coordination.workflow_orchestrator import execute_workflow
from src.agents.simple_agents import (
    code_analysis_agent,
    requirement_analysis_agent,
    test_selection_agent,
    reflection_agent,
    execution_agent
)


async def example_workflow():
    """Example of running the complete workflow."""
    print("🚀 Running Smarter Case Workflow Example")
    print("=" * 50)
    
    # Example parameters
    commit_hash = "abc123def456"
    branch = "main"
    time_range = "24h"
    project_key = "PROJ"
    
    try:
        # Execute the complete workflow
        result = await execute_workflow(
            commit_hash=commit_hash,
            branch=branch,
            time_range=time_range,
            project_key=project_key
        )
        
        print(f"✅ Workflow completed with status: {result['status']}")
        print(f"📊 Total steps executed: {len(result.get('results', {}))}")
        
        # Display results
        if result['status'] == 'completed':
            print("\n📋 Execution Results:")
            for step_key, step_result in result['results'].items():
                print(f"\n{step_key}:")
                print(f"  Agent: {step_result['agent']}")
                print(f"  Output: {step_result['output'][:200]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        return None


def example_individual_agents():
    """Example of running individual agents."""
    print("\n🔧 Running Individual Agents Example")
    print("=" * 50)
    
    # Example 1: Code Analysis Agent
    print("\n1. Code Analysis Agent:")
    code_result = code_analysis_agent("abc123def456", "main")
    print(f"   Status: {code_result['status']}")
    print(f"   Output: {code_result['output'][:100]}...")
    
    # Example 2: Requirement Analysis Agent
    print("\n2. Requirement Analysis Agent:")
    req_result = requirement_analysis_agent("24h", "PROJ")
    print(f"   Status: {req_result['status']}")
    print(f"   Output: {req_result['output'][:100]}...")
    
    # Example 3: Test Selection Agent
    print("\n3. Test Selection Agent:")
    test_result = test_selection_agent(code_result, req_result)
    print(f"   Status: {test_result['status']}")
    print(f"   Output: {test_result['output'][:100]}...")
    
    # Example 4: Reflection Agent
    print("\n4. Reflection Agent:")
    reflection_result = reflection_agent(test_result)
    print(f"   Status: {reflection_result['status']}")
    print(f"   Output: {reflection_result['output'][:100]}...")
    
    # Example 5: Execution Agent
    print("\n5. Execution Agent:")
    exec_result = execution_agent(reflection_result, "github-actions")
    print(f"   Status: {exec_result['status']}")
    print(f"   Output: {exec_result['output'][:100]}...")


def example_cli_usage():
    """Example of CLI usage."""
    print("\n💻 CLI Usage Example")
    print("=" * 50)
    
    cli_examples = [
        "# Basic usage",
        "python -m src.main --commit-hash abc123def456",
        "",
        "# With custom parameters",
        "python -m src.main --commit-hash abc123def456 --branch feature-branch --time-range 48h",
        "",
        "# With output file",
        "python -m src.main --commit-hash abc123def456 --output-file results.json",
        "",
        "# Verbose output",
        "python -m src.main --commit-hash abc123def456 --verbose",
        "",
        "# JSON output format",
        "python -m src.main --commit-hash abc123def456 --output-format json"
    ]
    
    for example in cli_examples:
        print(example)


async def main():
    """Main example function."""
    print("🧪 Smarter Case - Intelligent Test Case Selection")
    print("=" * 60)
    
    # Run individual agents example
    example_individual_agents()
    
    # Run CLI usage example
    example_cli_usage()
    
    # Run complete workflow example
    await example_workflow()
    
    print("\n✅ Examples completed!")
    print("\n📚 Next Steps:")
    print("1. Configure your .env file with API keys")
    print("2. Run: python -m src.main --commit-hash YOUR_COMMIT_HASH")
    print("3. Check the results and integrate with your CI/CD pipeline")


if __name__ == "__main__":
    asyncio.run(main())
