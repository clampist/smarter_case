"""
Jira API tools for fetching and analyzing requirement changes.
"""
import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from ..utils.logger import get_logger


@dataclass
class JiraIssue:
    """Represents a Jira issue."""
    id: str
    key: str
    summary: str
    description: str
    status: str
    priority: str
    issue_type: str
    assignee: Optional[str]
    reporter: str
    created: str
    updated: str
    labels: List[str]
    components: List[str]
    fix_versions: List[str]
    custom_fields: Dict[str, Any]


@dataclass
class JiraProject:
    """Represents a Jira project."""
    id: str
    key: str
    name: str
    description: str
    project_type: str
    lead: str


class JiraAPIError(Exception):
    """Custom exception for Jira API errors."""
    pass


class JiraTools:
    """
    Jira API tools for fetching requirement changes and project information.
    
    This class provides functionality to:
    - Fetch issues from Jira projects
    - Filter issues by time range and criteria
    - Analyze requirement changes and their business impact
    - Get project information and configurations
    """
    
    def __init__(
        self,
        jira_url: str,
        username: str,
        api_token: str,
        timeout: int = 30
    ):
        """
        Initialize Jira tools.
        
        Args:
            jira_url: Jira instance URL (e.g., https://company.atlassian.net)
            username: Jira username or email
            api_token: Jira API token
            timeout: Request timeout in seconds
        """
        self.jira_url = jira_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.timeout = timeout
        self.logger = get_logger("jira_tools")
        
        # Create authentication header
        self.auth_header = {
            'Authorization': f'Basic {self._encode_auth(username, api_token)}',
            'Content-Type': 'application/json'
        }
        
        self.logger.info(f"Initialized Jira tools for {jira_url}")
    
    def _encode_auth(self, username: str, api_token: str) -> str:
        """Encode username and API token for basic authentication."""
        import base64
        credentials = f"{username}:{api_token}"
        return base64.b64encode(credentials.encode()).decode()
    
    async def get_project_info(self, project_key: str) -> JiraProject:
        """
        Get project information.
        
        Args:
            project_key: Jira project key
            
        Returns:
            JiraProject: Project information
        """
        url = f"{self.jira_url}/rest/api/3/project/{project_key}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=self.auth_header,
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return JiraProject(
                            id=data['id'],
                            key=data['key'],
                            name=data['name'],
                            description=data.get('description', ''),
                            project_type=data['projectTypeKey'],
                            lead=data['lead']['displayName']
                        )
                    else:
                        error_text = await response.text()
                        raise JiraAPIError(f"Failed to get project info: {response.status} - {error_text}")
        
        except aiohttp.ClientError as e:
            raise JiraAPIError(f"Network error getting project info: {e}")
    
    async def search_issues(
        self,
        project_key: str,
        jql_query: Optional[str] = None,
        max_results: int = 100,
        fields: Optional[List[str]] = None
    ) -> List[JiraIssue]:
        """
        Search for issues using JQL query.
        
        Args:
            project_key: Jira project key
            jql_query: JQL query string (optional)
            max_results: Maximum number of results to return
            fields: Specific fields to retrieve
            
        Returns:
            List[JiraIssue]: List of matching issues
        """
        url = f"{self.jira_url}/rest/api/3/search"
        
        # Default JQL query if none provided
        if not jql_query:
            jql_query = f"project = {project_key} ORDER BY updated DESC"
        
        # Default fields to retrieve
        if not fields:
            fields = [
                'id', 'key', 'summary', 'description', 'status', 'priority',
                'issuetype', 'assignee', 'reporter', 'created', 'updated',
                'labels', 'components', 'fixVersions'
            ]
        
        payload = {
            'jql': jql_query,
            'maxResults': max_results,
            'fields': fields,
            'expand': ['changelog']
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=self.auth_header,
                    json=payload,
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        issues = []
                        
                        for issue_data in data.get('issues', []):
                            issue = self._parse_issue(issue_data)
                            issues.append(issue)
                        
                        self.logger.info(f"Retrieved {len(issues)} issues for project {project_key}")
                        return issues
                    else:
                        error_text = await response.text()
                        raise JiraAPIError(f"Failed to search issues: {response.status} - {error_text}")
        
        except aiohttp.ClientError as e:
            raise JiraAPIError(f"Network error searching issues: {e}")
    
    async def get_issues_updated_since(
        self,
        project_key: str,
        since_hours: int = 24,
        issue_types: Optional[List[str]] = None
    ) -> List[JiraIssue]:
        """
        Get issues updated within the specified time range.
        
        Args:
            project_key: Jira project key
            since_hours: Number of hours to look back
            issue_types: List of issue types to filter (e.g., ['Story', 'Task', 'Bug'])
            
        Returns:
            List[JiraIssue]: List of recently updated issues
        """
        # Calculate the date threshold
        since_date = datetime.now() - timedelta(hours=since_hours)
        since_date_str = since_date.strftime('%Y-%m-%d %H:%M')
        
        # Build JQL query
        jql_parts = [f"project = {project_key}"]
        jql_parts.append(f"updated >= '{since_date_str}'")
        
        if issue_types:
            issue_types_str = ', '.join([f'"{itype}"' for itype in issue_types])
            jql_parts.append(f"issuetype IN ({issue_types_str})")
        
        jql_query = " AND ".join(jql_parts) + " ORDER BY updated DESC"
        
        return await self.search_issues(project_key, jql_query)
    
    async def get_requirement_changes(
        self,
        project_key: str,
        time_range: str = "24h",
        priority_levels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get requirement changes and analyze their business impact.
        
        Args:
            project_key: Jira project key
            time_range: Time range to analyze (e.g., "24h", "7d", "1w")
            priority_levels: Priority levels to filter (e.g., ["High", "Critical"])
            
        Returns:
            Dict containing requirement changes analysis
        """
        # Parse time range
        hours = self._parse_time_range(time_range)
        
        # Get recent issues
        issues = await self.get_issues_updated_since(
            project_key,
            since_hours=hours,
            issue_types=['Story', 'Task', 'Bug', 'Epic', 'Subtask']
        )
        
        # Filter by priority if specified
        if priority_levels:
            issues = [
                issue for issue in issues 
                if issue.priority in priority_levels
            ]
        
        # Analyze changes
        analysis = {
            'time_range': time_range,
            'project_key': project_key,
            'total_issues': len(issues),
            'issues_by_type': self._group_issues_by_type(issues),
            'issues_by_priority': self._group_issues_by_priority(issues),
            'issues_by_status': self._group_issues_by_status(issues),
            'recent_changes': [
                {
                    'key': issue.key,
                    'summary': issue.summary,
                    'type': issue.issue_type,
                    'priority': issue.priority,
                    'status': issue.status,
                    'updated': issue.updated,
                    'assignee': issue.assignee,
                    'labels': issue.labels,
                    'components': issue.components
                }
                for issue in issues
            ],
            'business_impact': self._analyze_business_impact(issues),
            'risk_assessment': self._assess_risk_level(issues)
        }
        
        self.logger.info(f"Analyzed {len(issues)} requirement changes for project {project_key}")
        return analysis
    
    def _parse_time_range(self, time_range: str) -> int:
        """Parse time range string to hours."""
        time_range = time_range.lower().strip()
        
        if time_range.endswith('h'):
            return int(time_range[:-1])
        elif time_range.endswith('d'):
            return int(time_range[:-1]) * 24
        elif time_range.endswith('w'):
            return int(time_range[:-1]) * 24 * 7
        else:
            # Default to 24 hours
            return 24
    
    def _parse_issue(self, issue_data: Dict[str, Any]) -> JiraIssue:
        """Parse Jira issue data into JiraIssue object."""
        fields = issue_data.get('fields', {})
        
        # Extract assignee name if exists
        assignee = None
        if fields.get('assignee'):
            assignee = fields['assignee'].get('displayName')
        
        # Extract reporter name
        reporter = fields.get('reporter', {}).get('displayName', 'Unknown')
        
        # Extract labels
        labels = fields.get('labels', [])
        
        # Extract components
        components = [
            comp['name'] for comp in fields.get('components', [])
        ]
        
        # Extract fix versions
        fix_versions = [
            version['name'] for version in fields.get('fixVersions', [])
        ]
        
        return JiraIssue(
            id=issue_data['id'],
            key=issue_data['key'],
            summary=fields.get('summary', ''),
            description=fields.get('description', ''),
            status=fields.get('status', {}).get('name', 'Unknown'),
            priority=fields.get('priority', {}).get('name', 'Medium'),
            issue_type=fields.get('issuetype', {}).get('name', 'Task'),
            assignee=assignee,
            reporter=reporter,
            created=fields.get('created', ''),
            updated=fields.get('updated', ''),
            labels=labels,
            components=components,
            fix_versions=fix_versions,
            custom_fields={}
        )
    
    def _group_issues_by_type(self, issues: List[JiraIssue]) -> Dict[str, int]:
        """Group issues by type."""
        groups = {}
        for issue in issues:
            issue_type = issue.issue_type
            groups[issue_type] = groups.get(issue_type, 0) + 1
        return groups
    
    def _group_issues_by_priority(self, issues: List[JiraIssue]) -> Dict[str, int]:
        """Group issues by priority."""
        groups = {}
        for issue in issues:
            priority = issue.priority
            groups[priority] = groups.get(priority, 0) + 1
        return groups
    
    def _group_issues_by_status(self, issues: List[JiraIssue]) -> Dict[str, int]:
        """Group issues by status."""
        groups = {}
        for issue in issues:
            status = issue.status
            groups[status] = groups.get(status, 0) + 1
        return groups
    
    def _analyze_business_impact(self, issues: List[JiraIssue]) -> Dict[str, Any]:
        """Analyze business impact of requirement changes."""
        impact_analysis = {
            'high_priority_count': len([i for i in issues if i.priority in ['High', 'Critical']]),
            'new_issues_count': len([i for i in issues if i.status == 'New']),
            'in_progress_count': len([i for i in issues if i.status in ['In Progress', 'Active']]),
            'completed_count': len([i for i in issues if i.status in ['Done', 'Closed', 'Resolved']]),
            'blocked_count': len([i for i in issues if i.status == 'Blocked']),
            'affected_components': list(set([
                comp for issue in issues for comp in issue.components
            ])),
            'affected_versions': list(set([
                version for issue in issues for version in issue.fix_versions
            ]))
        }
        
        return impact_analysis
    
    def _assess_risk_level(self, issues: List[JiraIssue]) -> str:
        """Assess overall risk level based on issues."""
        if not issues:
            return "low"
        
        high_priority_count = len([i for i in issues if i.priority in ['High', 'Critical']])
        blocked_count = len([i for i in issues if i.status == 'Blocked'])
        total_issues = len(issues)
        
        high_priority_ratio = high_priority_count / total_issues
        blocked_ratio = blocked_count / total_issues
        
        if high_priority_ratio > 0.5 or blocked_ratio > 0.3:
            return "high"
        elif high_priority_ratio > 0.2 or blocked_ratio > 0.1:
            return "medium"
        else:
            return "low"
    
    async def test_connection(self) -> bool:
        """Test connection to Jira API."""
        try:
            # Try to get server info
            url = f"{self.jira_url}/rest/api/3/serverInfo"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=self.auth_header,
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        self.logger.info("Successfully connected to Jira API")
                        return True
                    else:
                        self.logger.error(f"Failed to connect to Jira API: {response.status}")
                        return False
        
        except Exception as e:
            self.logger.error(f"Error testing Jira connection: {e}")
            return False
