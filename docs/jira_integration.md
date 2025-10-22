 summaries
# Jira API Integration

This document describes how to use the Jira API integration with the Smarter Case system.

## Overview

The Jira integration allows the Requirement Analysis Agent to fetch real requirement changes from Jira projects, providing more accurate analysis for test case selection.

## Features

- **Real-time Data**: Fetch actual requirement changes from Jira
- **Flexible Filtering**: Filter issues by time range, priority, and type
- **Business Impact Analysis**: Analyze the business impact of requirement changes
- **Risk Assessment**: Assess risk levels based on issue characteristics
- **Fallback Support**: Gracefully fallback to mock data if Jira is unavailable

## Configuration

### Environment Variables

Set the following environment variables in your `.env` file:

```bash
# Jira Configuration
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your-api-token
JIRA_PROJECT_KEY=PROJ
```

### Getting API Token

1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a label (e.g., "Smarter Case")
4. Copy the generated token

## Usage

### Basic Usage

```python
from src.agents.simple_agents import requirement_analysis_agent

# Use Jira integration
result = requirement_analysis_agent(
    time_range="24h",
    project_key="PROJ",
    use_jira=True,
    jira_config={
        'url': 'https://your-company.atlassian.net',
        'username': 'your-email@company.com',
        'api_token': 'your-api-token'
    }
)
```

### Mock Data Fallback

```python
# Use mock data (no Jira connection required)
result = requirement_analysis_agent(
    time_range="24h",
    project_key="PROJ",
    use_jira=False
)
```

## API Reference

### JiraTools Class

The `JiraTools` class provides the core functionality for interacting with Jira:

```python
from src.tools.jira_tools import JiraTools

jira_tools = JiraTools(
    jira_url="https://your-company.atlassian.net",
    username="your-email@company.com",
    api_token="your-api-token"
)

# Test connection
await jira_tools.test_connection()

# Get project info
project_info = await jira_tools.get_project_info("PROJ")

# Search issues
issues = await jira_tools.search_issues("PROJ", jql_query="status = 'In Progress'")

# Get recent changes
changes = await jira_tools.get_requirement_changes("PROJ", time_range="24h")
```

### Key Methods

- `test_connection()`: Test connection to Jira API
- `get_project_info(project_key)`: Get project information
- `search_issues(project_key, jql_query)`: Search issues using JQL
- `get_issues_updated_since(project_key, since_hours)`: Get recently updated issues
- `get_requirement_changes(project_key, time_range)`: Get requirement changes analysis

## Error Handling

The integration includes comprehensive error handling:

- **Connection Errors**: Gracefully fallback to mock data
- **Authentication Errors**: Clear error messages for invalid credentials
- **Rate Limiting**: Respects Jira API rate limits
- **Timeout Handling**: Configurable timeouts for API calls

## Examples

See `examples/jira_integration_example.py` for a complete working example.

## Troubleshooting

### Common Issues

1. **404 Error**: Check your Jira URL format
2. **401 Unauthorized**: Verify your username and API token
3. **403 Forbidden**: Ensure you have access to the project
4. **Rate Limited**: Wait and retry, or increase timeout

### Debug Mode

Enable debug logging to see detailed API interactions:

```python
import logging
logging.getLogger("jira_tools").setLevel(logging.DEBUG)
```

## Security Notes

- Never commit API tokens to version control
- Use environment variables for sensitive configuration
- Regularly rotate API tokens
- Limit API token permissions to necessary projects only
