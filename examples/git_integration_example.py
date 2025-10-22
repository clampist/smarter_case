#!/usr/bin/env python3
"""
Example demonstrating enhanced Git integration with the Smarter Case system.
"""
import os
import sys
import asyncio
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.simple_agents import code_analysis_agent
from src.tools.git_tools import GitAnalyzer


async def test_git_analyzer():
    """Test Git analyzer functionality."""
    print("🔧 Testing Git Analyzer")
    print("=" * 50)
    
    try:
        git_analyzer = GitAnalyzer()
        
        # Get repository info
        repo_info = await git_analyzer.get_repository_info()
        print(f"📋 Repository: {repo_info.url}")
        print(f"🌿 Current Branch: {repo_info.current_branch}")
        print(f"🔗 Remotes: {list(repo_info.remotes.keys())}")
        
        # Get recent commits
        recent_commits = await git_analyzer.get_recent_commits(count=5)
        print(f"📊 Recent Commits: {len(recent_commits)}")
        
        for i, commit in enumerate(recent_commits[:3]):
            print(f"  {i+1}. {commit.hash[:8]}: {commit.message[:50]}...")
        
        # Get last commit hash for analysis
        if recent_commits:
            last_commit_hash = recent_commits[0].hash
            print(f"\n🔍 Analyzing last commit: {last_commit_hash[:8]}")
            
            # Get comprehensive commit analysis
            commit_analysis = await git_analyzer.get_comprehensive_commit_analysis(last_commit_hash)
            
            print(f"📈 Impact Assessment:")
            print(f"  - Risk Level: {commit_analysis['risk_level']}")
            print(f"  - Business Impact: {commit_analysis['business_impact']}")
            print(f"  - Files Changed: {len(commit_analysis['files_changed'])}")
            print(f"  - Code Changes: {commit_analysis['impact_assessment']['change_count']}")
            
            if commit_analysis['test_recommendations']['recommended_tests']:
                print(f"  - Recommended Tests: {', '.join(commit_analysis['test_recommendations']['recommended_tests'][:3])}")
            
            return last_commit_hash
        else:
            print("⚠️ No commits found in repository")
            return None
            
    except Exception as e:
        print(f"❌ Error testing Git analyzer: {e}")
        return None


def test_code_analysis_with_git():
    """Test code analysis agent with Git integration."""
    print("\n🔍 Testing Code Analysis with Git Integration")
    print("=" * 50)
    
    try:
        # Test with Git analysis enabled
        result = code_analysis_agent(
            commit_hash="HEAD",
            branch="main",
            model="mock",  # Use mock for testing
            use_git_analysis=True  # Enable Git integration
        )
        
        print("✅ Code Analysis with Git Integration:")
        print(f"Status: {result['status']}")
        print(f"Output: {result['output'][:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in code analysis with Git: {e}")
        return False


def test_code_analysis_mock():
    """Test code analysis agent with mock data."""
    print("\n🎭 Testing Code Analysis with Mock Data")
    print("=" * 50)
    
    try:
        result = code_analysis_agent(
            commit_hash="abc123def456",
            branch="main",
            model="mock",  # Use mock for testing
            use_git_analysis=False  # Use mock data
        )
        
        print("✅ Code Analysis with Mock Data:")
        print(f"Status: {result['status']}")
        print(f"Output: {result['output'][:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in code analysis with mock: {e}")
        return False


async def test_branch_comparison():
    """Test branch comparison functionality."""
    print("\n🌿 Testing Branch Comparison")
    print("=" * 50)
    
    try:
        git_analyzer = GitAnalyzer()
        
        # Get all branches
        repo_info = await git_analyzer.get_repository_info()
        branches = [branch.name for branch in repo_info.branches]
        
        print(f"📋 Available branches: {branches}")
        
        if len(branches) >= 2:
            # Compare first two branches
            base_branch = branches[0]
            compare_branch = branches[1]
            
            comparison = await git_analyzer.compare_branches(base_branch, compare_branch)
            
            print(f"🔄 Comparing {base_branch} vs {compare_branch}:")
            print(f"  - Ahead: {comparison['ahead_count']} commits")
            print(f"  - Behind: {comparison['behind_count']} commits")
            print(f"  - Different files: {len(comparison['different_files'])}")
            print(f"  - Has conflicts: {comparison['has_conflicts']}")
            
            if comparison['new_commits']:
                print(f"  - New commits: {len(comparison['new_commits'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in branch comparison: {e}")
        return False


async def main():
    """Main function to run all tests."""
    print("🧪 Smarter Case - Git Integration Example")
    print("=" * 60)
    
    # Test 1: Git analyzer
    last_commit_hash = await test_git_analyzer()
    
    # Test 2: Code analysis with mock data
    mock_success = test_code_analysis_mock()
    
    # Test 3: Code analysis with Git (only if we have a commit)
    git_success = True
    if last_commit_hash:
        git_success = test_code_analysis_with_git()
    else:
        print("\n⚠️ Skipping Git integration test due to no commits found")
    
    # Test 4: Branch comparison
    branch_success = await test_branch_comparison()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    print(f"Git Analyzer: {'✅ Success' if last_commit_hash else '❌ Failed'}")
    print(f"Mock Analysis: {'✅ Success' if mock_success else '❌ Failed'}")
    print(f"Git Analysis: {'✅ Success' if git_success else '❌ Failed'}")
    print(f"Branch Comparison: {'✅ Success' if branch_success else '❌ Failed'}")
    
    if last_commit_hash and mock_success and git_success and branch_success:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed. Check your Git repository setup.")
    
    print("\n📝 Git Integration Features:")
    print("- ✅ Comprehensive commit analysis")
    print("- ✅ Impact assessment and risk analysis")
    print("- ✅ Business impact evaluation")
    print("- ✅ Test recommendations generation")
    print("- ✅ Branch comparison and conflict detection")
    print("- ✅ Repository information extraction")
    print("- ✅ Module and component impact analysis")


if __name__ == "__main__":
    asyncio.run(main())
