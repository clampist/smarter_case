# Git Integration

This document describes the enhanced Git integration with the Smarter Case system.

## Overview

The Git integration provides comprehensive code change analysis, impact assessment, and test recommendations based on actual Git commits and repository information.

## Features

- **Comprehensive Commit Analysis**: Detailed analysis of Git commits including file changes, impact assessment, and risk evaluation
- **Impact Assessment**: Automatic assessment of business impact and risk levels
- **Test Recommendations**: Intelligent generation of test recommendations based on code changes
- **Branch Comparison**: Compare branches and detect conflicts
- **Repository Analysis**: Extract repository information, branches, and commit history
- **Module Impact Analysis**: Identify affected modules and components

## Architecture

### Data Models

The Git integration includes several data models:

- **GitCommit**: Represents a Git commit with metadata
- **GitDiff**: Represents file-level changes
- **GitBranch**: Represents branch information
- **GitRepository**: Represents repository information
- **CodeChange**: Represents detailed code change analysis

### GitAnalyzer Class

The `GitAnalyzer` class provides the core functionality:

```python
from src.tools.git_tools import GitAnalyzer

git_analyzer = GitAnalyzer(repo_path=".")
```

## Usage

### Basic Usage

```python
from src.agents.simple_agents import code_analysis_agent

# Use Git integration
result = code_analysis_agent(
    commit_hash="abc123def456",
    branch="main",
    use_git_analysis=True
)

# Use mock data
result = code_analysis_agent(
    commit_hash="abc123def456",
    branch="main",
    use_git_analysis=False
)
```

### Advanced Git Analysis

```python
from src.tools.git_tools import GitAnalyzer

git_analyzer = GitAnalyzer()

# Get comprehensive commit analysis
analysis = await git_analyzer.get_comprehensive_commit_analysis("abc123def456")

# Get repository information
repo_info = await git_analyzer.get_repository_info()

# Compare branches
comparison = await git_analyzer.compare_branches("main", "feature-branch")

# Get recent commits
commits = await git_analyzer.get_recent_commits(count=10)
```

## Analysis Features

### Impact Assessment

The system automatically assesses:

- **Risk Level**: High, medium, or low based on change complexity and affected modules
- **Business Impact**: High, medium, or low based on affected business domains
- **Complexity Score**: Numerical score indicating change complexity
- **Affected Modules**: List of modules impacted by changes

### Module Detection

The system automatically identifies affected modules based on file patterns:

- **API**: `api/`, `src/api/`, `app/api/`, `routes/`, `controllers/`
- **UI**: `ui/`, `frontend/`, `src/ui/`, `components/`, `views/`, `templates/`
- **Database**: `db/`, `database/`, `models/`, `migrations/`, `schema/`
- **Config**: `config/`, `settings/`, `conf/`, `.env`, `docker/`
- **Tests**: `tests/`, `test/`, `spec/`, `__tests__/`, `e2e/`
- **Utils**: `utils/`, `helpers/`, `lib/`, `common/`
- **Services**: `services/`, `src/services/`, `business/`
- **Middleware**: `middleware/`, `src/middleware/`, `interceptors/`

### Test Recommendations

The system generates intelligent test recommendations based on:

- **Module Type**: Different test types for different modules
- **Change Type**: Added, modified, or deleted files
- **Risk Level**: Critical path tests for high-risk changes
- **Business Impact**: Comprehensive testing for high-impact changes

## API Reference

### GitAnalyzer Methods

#### Core Analysis Methods

- `get_comprehensive_commit_analysis(commit_hash)`: Get detailed commit analysis
- `get_commit_info(commit_hash)`: Get basic commit information
- `get_commit_diff(commit_hash)`: Get commit diff
- `get_files_changed(commit_hash)`: Get list of changed files

#### Repository Methods

- `get_repository_info()`: Get comprehensive repository information
- `get_recent_commits(count, branch)`: Get recent commits
- `get_branch_info(branch)`: Get branch information
- `compare_branches(base_branch, compare_branch)`: Compare two branches

#### Analysis Methods

- `analyze_commit_impact(commit_hash)`: Analyze commit impact
- `_analyze_code_changes(diff_output)`: Analyze code changes from diff
- `_assess_business_impact(change)`: Assess business impact
- `_assess_risk_level(change)`: Assess risk level
- `_generate_test_recommendations(changes)`: Generate test recommendations

### Code Analysis Agent Integration

The `code_analysis_agent` function has been enhanced to use Git analysis:

```python
async def code_analysis_agent(
    commit_hash: str,
    branch: str = "main",
    model: Optional[str] = None,
    use_git_analysis: bool = True
) -> Dict[str, Any]:
```

## Configuration

### Module Patterns

You can customize module detection patterns:

```python
git_analyzer = GitAnalyzer()
git_analyzer.module_patterns = {
    'api': ['api/', 'src/api/', 'routes/'],
    'ui': ['ui/', 'frontend/', 'components/'],
    # Add custom patterns
}
```

## Examples

### Comprehensive Commit Analysis

```python
from src.tools.git_tools import GitAnalyzer

async def analyze_commit():
    git_analyzer = GitAnalyzer()
    
    # Get comprehensive analysis
    analysis = await git_analyzer.get_comprehensive_commit_analysis("abc123def456")
    
    print(f"Risk Level: {analysis['risk_level']}")
    print(f"Business Impact: {analysis['business_impact']}")
    print(f"Files Changed: {len(analysis['files_changed'])}")
    print(f"Recommended Tests: {analysis['test_recommendations']['recommended_tests']}")
```

### Branch Comparison

```python
async def compare_branches():
    git_analyzer = GitAnalyzer()
    
    comparison = await git_analyzer.compare_branches("main", "feature-branch")
    
    print(f"Ahead: {comparison['ahead_count']} commits")
    print(f"Behind: {comparison['behind_count']} commits")
    print(f"Different files: {len(comparison['different_files'])}")
    print(f"Has conflicts: {comparison['has_conflicts']}")
```

## Error Handling

The Git integration includes comprehensive error handling:

- **Git Command Errors**: Graceful handling of failed Git commands
- **Repository Errors**: Fallback to mock data when repository is unavailable
- **Analysis Errors**: Error recovery with detailed error messages
- **Timeout Handling**: Configurable timeouts for long-running operations

## Performance Considerations

- **Async Operations**: All Git operations are asynchronous for better performance
- **Caching**: Consider implementing caching for frequently accessed data
- **Batch Operations**: Use batch operations for multiple commit analysis
- **Memory Management**: Large repositories may require memory optimization

## Troubleshooting

### Common Issues

1. **Git Command Not Found**: Ensure Git is installed and in PATH
2. **Repository Not Found**: Check repository path and permissions
3. **Permission Errors**: Ensure read access to repository files
4. **Large Repository Performance**: Consider limiting analysis scope for large repositories

### Debug Mode

Enable debug logging to see detailed Git operations:

```python
import logging
logging.getLogger("git_analyzer").setLevel(logging.DEBUG)
```

## Integration with CI/CD

The Git integration is designed to work seamlessly with CI/CD pipelines:

- **Environment Variables**: Use `GIT_COMMIT_HASH` and `GIT_BRANCH` from CI/CD
- **Automated Analysis**: Automatically analyze commits in CI/CD pipelines
- **Test Recommendations**: Generate test commands for CI/CD execution
- **Impact Reporting**: Provide impact assessment for deployment decisions
