#!/usr/bin/env python3
"""
Example demonstrating Jira API integration with the Smarter Case system.
"""
import os
import sys
import asyncio
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.simple_agents import requirement_analysis_agent
from src.tools.jira_tools import JiraTools


async def test_jira_connection():
    """Test Jira API connection."""
    print("🔗 Testing Jira API Connection")
    print("=" * 50)
    
    # Jira configuration - replace with your actual values
    jira_config = {
        'url': os.getenv('JIRA_URL', 'https://your-company.atlassian.net'),
        'username': os.getenv('JIRA_USERNAME', 'your-email@company.com'),
        'api_token': os.getenv('JIRA_API_TOKEN', 'your-api-token')
    }
    
    try:
        jira_tools = JiraTools(
            jira_url=jira_config['url'],
            username=jira_config['username'],
            api_token=jira_config['api_token']
        )
        
        # Test connection
        if await jira_tools.test_connection():
            print("✅ Successfully connected to Jira API")
            
            # Get project info
            project_key = os.getenv('JIRA_PROJECT_KEY', 'PROJ')
            project_info = await jira_tools.get_project_info(project_key)
            print(f"📋 Project: {project_info.name} ({project_info.key})")
            
            # Get recent issues
            issues = await jira_tools.get_issues_updated_since(
                project_key=project_key,
                since_hours=24
            )
            print(f"📊 Found {len(issues)} issues updated in the last 24 hours")
            
            # Show recent issues
            for issue in issues[:5]:  # Show first 5 issues
                print(f"  - {issue.key}: {issue.summary} ({issue.status})")
            
            return True
        else:
            print("❌ Failed to connect to Jira API")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Jira connection: {e}")
        return False


def test_requirement_analysis_with_jira():
    """Test requirement analysis agent with Jira integration."""
    print("\n📋 Testing Requirement Analysis with Jira Integration")
    print("=" * 50)
    
    # Jira configuration
    jira_config = {
        'url': os.getenv('JIRA_URL', 'https://your-company.atlassian.net'),
        'username': os.getenv('JIRA_USERNAME', 'your-email@company.com'),
        'api_token': os.getenv('JIRA_API_TOKEN', 'your-api-token')
    }
    
    # Test with Jira integration enabled
    try:
        result = requirement_analysis_agent(
            time_range="24h",
            project_key=os.getenv('JIRA_PROJECT_KEY', 'PROJ'),
            model="mock",  # Use mock for testing
            use_jira=True,  # Enable Jira integration
            jira_config=jira_config
        )
        
        print("✅ Requirement Analysis with Jira Integration:")
        print(f"Status: {result['status']}")
        print(f"Output: {result['output'][:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in requirement analysis: {e}")
        return False


def test_requirement_analysis_mock():
    """Test requirement analysis agent with mock data."""
    print("\n🎭 Testing Requirement Analysis with Mock Data")
    print("=" * 50)
    
    try:
        result = requirement_analysis_agent(
            time_range="24h",
            project_key="PROJ",
            model="mock",  # Use mock for testing
            use_jira=False  # Use mock data
        )
        
        print("✅ Requirement Analysis with Mock Data:")
        print(f"Status: {result['status']}")
        print(f"Output: {result['output'][:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in requirement analysis: {e}")
        return False


async def main():
    """Main function to run all tests."""
    print("🧪 Smarter Case - Jira Integration Example")
    print("=" * 60)
    
    # Test 1: Jira connection
    jira_connected = await test_jira_connection()
    
    # Test 2: Requirement analysis with mock data
    mock_success = test_requirement_analysis_mock()
    
    # Test 3: Requirement analysis with Jira (only if connection successful)
    jira_success = True
    if jira_connected:
        jira_success = test_requirement_analysis_with_jira()
    else:
        print("\n⚠️ Skipping Jira integration test due to connection failure")
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    print(f"Jira Connection: {'✅ Success' if jira_connected else '❌ Failed'}")
    print(f"Mock Analysis: {'✅ Success' if mock_success else '❌ Failed'}")
    print(f"Jira Analysis: {'✅ Success' if jira_success else '❌ Failed'}")
    
    if jira_connected and mock_success and jira_success:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed. Check your configuration.")
    
    print("\n📝 Configuration Notes:")
    print("To use real Jira integration, set these environment variables:")
    print("- JIRA_URL: Your Jira instance URL")
    print("- JIRA_USERNAME: Your Jira username or email")
    print("- JIRA_API_TOKEN: Your Jira API token")
    print("- JIRA_PROJECT_KEY: The project key to analyze")


if __name__ == "__main__":
    asyncio.run(main())
