"""
Git tools for analyzing code changes and repository information.
"""
import asyncio
import subprocess
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ..utils.logger import get_logger


@dataclass
class GitCommit:
    """Represents a Git commit."""
    hash: str
    message: str
    author: str
    date: str
    files_changed: List[str]


@dataclass
class GitDiff:
    """Represents a Git diff."""
    file_path: str
    change_type: str  # added, modified, deleted
    lines_added: int
    lines_removed: int
    content: str


@dataclass
class GitBranch:
    """Represents a Git branch."""
    name: str
    is_current: bool
    last_commit_hash: str
    last_commit_message: str
    last_commit_author: str
    last_commit_date: str
    ahead_count: int = 0
    behind_count: int = 0


@dataclass
class GitRepository:
    """Represents a Git repository."""
    url: str
    current_branch: str
    branches: List[GitBranch]
    remotes: Dict[str, str]
    last_commit: Optional[GitCommit] = None


@dataclass
class CodeChange:
    """Represents a code change with detailed analysis."""
    file_path: str
    change_type: str
    lines_added: int
    lines_removed: int
    complexity_change: int
    affected_modules: List[str]
    business_impact: str
    risk_level: str
    test_impact: List[str]


class GitAnalyzer:
    """
    Enhanced Git analysis tools for the Smarter Case system.
    
    This class provides functionality to:
    - Analyze Git commits and changes with detailed impact assessment
    - Get comprehensive repository information
    - Extract and analyze diff information
    - Identify affected files, modules, and business domains
    - Assess code change complexity and risk levels
    - Generate test impact recommendations
    - Support both local and remote repository analysis
    """
    
    def __init__(self, repo_path: str = "."):
        """
        Initialize Git analyzer.
        
        Args:
            repo_path: Path to the Git repository (defaults to current directory)
        """
        self.repo_path = repo_path
        self.logger = get_logger("git_analyzer")
        
        # Module patterns for impact analysis
        self.module_patterns = {
            'api': ['api/', 'src/api/', 'app/api/', 'routes/', 'controllers/'],
            'ui': ['ui/', 'frontend/', 'src/ui/', 'components/', 'views/', 'templates/'],
            'database': ['db/', 'database/', 'models/', 'migrations/', 'schema/'],
            'config': ['config/', 'settings/', 'conf/', '.env', 'docker/'],
            'tests': ['tests/', 'test/', 'spec/', '__tests__/', 'e2e/'],
            'utils': ['utils/', 'helpers/', 'lib/', 'common/'],
            'services': ['services/', 'src/services/', 'business/'],
            'middleware': ['middleware/', 'src/middleware/', 'interceptors/']
        }
    
    async def get_commit_info(self, commit_hash: str) -> GitCommit:
        """
        Get information about a specific commit.
        
        Args:
            commit_hash: Git commit hash
            
        Returns:
            GitCommit: Commit information
        """
        try:
            # Get commit information using git log
            cmd = [
                "git", "log", "--format=%H|%s|%an|%ad", "--date=iso",
                "-1", commit_hash
            ]
            
            result = await self._run_git_command(cmd)
            
            if not result.strip():
                raise ValueError(f"Commit {commit_hash} not found")
            
            # Parse the output
            parts = result.strip().split('|')
            if len(parts) < 4:
                raise ValueError(f"Invalid commit format: {result}")
            
            hash_val, message, author, date = parts[:4]
            
            # Get files changed
            files_changed = await self._get_files_changed(commit_hash)
            
            return GitCommit(
                hash=hash_val,
                message=message,
                author=author,
                date=date,
                files_changed=files_changed
            )
            
        except Exception as e:
            self.logger.error(f"Error getting commit info for {commit_hash}: {e}")
            raise
    
    async def get_commit_diff(self, commit_hash: str) -> str:
        """
        Get the diff for a specific commit.
        
        Args:
            commit_hash: Git commit hash
            
        Returns:
            str: Diff output
        """
        try:
            cmd = ["git", "show", "--format=", commit_hash]
            result = await self._run_git_command(cmd)
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting diff for {commit_hash}: {e}")
            raise
    
    async def get_files_changed(self, commit_hash: str) -> List[str]:
        """
        Get list of files changed in a commit.
        
        Args:
            commit_hash: Git commit hash
            
        Returns:
            List[str]: List of changed file paths
        """
        try:
            cmd = ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash]
            result = await self._run_git_command(cmd)
            
            files = [line.strip() for line in result.split('\n') if line.strip()]
            return files
            
        except Exception as e:
            self.logger.error(f"Error getting files changed for {commit_hash}: {e}")
            raise
    
    async def get_branch_info(self, branch: str = None) -> Dict[str, Any]:
        """
        Get information about the current branch or specified branch.
        
        Args:
            branch: Branch name (optional, defaults to current branch)
            
        Returns:
            Dict[str, Any]: Branch information
        """
        try:
            # Get current branch if not specified
            if not branch:
                cmd = ["git", "branch", "--show-current"]
                branch = (await self._run_git_command(cmd)).strip()
            
            # Get branch information
            cmd = ["git", "log", "--format=%H|%s|%an|%ad", "--date=iso", "-10", branch]
            result = await self._run_git_command(cmd)
            
            commits = []
            for line in result.split('\n'):
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 4:
                        commits.append({
                            'hash': parts[0],
                            'message': parts[1],
                            'author': parts[2],
                            'date': parts[3]
                        })
            
            return {
                'branch': branch,
                'recent_commits': commits,
                'total_commits': len(commits)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting branch info for {branch}: {e}")
            raise
    
    async def get_repo_info(self) -> Dict[str, Any]:
        """
        Get repository information.
        
        Returns:
            Dict[str, Any]: Repository information
        """
        try:
            # Get repository URL
            cmd = ["git", "remote", "get-url", "origin"]
            repo_url = await self._run_git_command(cmd)
            
            # Get current branch
            cmd = ["git", "branch", "--show-current"]
            current_branch = await self._run_git_command(cmd)
            
            # Get last commit
            cmd = ["git", "log", "--format=%H|%s|%an|%ad", "--date=iso", "-1"]
            last_commit = await self._run_git_command(cmd)
            
            last_commit_info = None
            if last_commit.strip():
                parts = last_commit.strip().split('|')
                if len(parts) >= 4:
                    last_commit_info = {
                        'hash': parts[0],
                        'message': parts[1],
                        'author': parts[2],
                        'date': parts[3]
                    }
            
            return {
                'repo_url': repo_url.strip(),
                'current_branch': current_branch.strip(),
                'last_commit': last_commit_info
            }
            
        except Exception as e:
            self.logger.error(f"Error getting repo info: {e}")
            raise
    
    async def analyze_commit_impact(self, commit_hash: str) -> Dict[str, Any]:
        """
        Analyze the impact of a commit.
        
        Args:
            commit_hash: Git commit hash
            
        Returns:
            Dict[str, Any]: Impact analysis
        """
        try:
            # Get commit info
            commit_info = await self.get_commit_info(commit_hash)
            
            # Get diff
            diff_output = await self.get_commit_diff(commit_hash)
            
            # Analyze the diff
            impact_analysis = self._analyze_diff_impact(diff_output)
            
            return {
                'commit': {
                    'hash': commit_info.hash,
                    'message': commit_info.message,
                    'author': commit_info.author,
                    'date': commit_info.date
                },
                'files_changed': commit_info.files_changed,
                'impact_analysis': impact_analysis
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing commit impact for {commit_hash}: {e}")
            raise
    
    def _analyze_diff_impact(self, diff_output: str) -> Dict[str, Any]:
        """
        Analyze the impact of a diff.
        
        Args:
            diff_output: Git diff output
            
        Returns:
            Dict[str, Any]: Impact analysis
        """
        lines_added = 0
        lines_removed = 0
        files_modified = 0
        files_added = 0
        files_deleted = 0
        
        current_file = None
        
        for line in diff_output.split('\n'):
            if line.startswith('diff --git'):
                if current_file:
                    files_modified += 1
                current_file = line.split()[-1] if len(line.split()) > 3 else None
            elif line.startswith('new file mode'):
                files_added += 1
            elif line.startswith('deleted file mode'):
                files_deleted += 1
            elif line.startswith('+') and not line.startswith('+++'):
                lines_added += 1
            elif line.startswith('-') and not line.startswith('---'):
                lines_removed += 1
        
        # Add the last file if we were processing one
        if current_file:
            files_modified += 1
        
        return {
            'lines_added': lines_added,
            'lines_removed': lines_removed,
            'files_modified': files_modified,
            'files_added': files_added,
            'files_deleted': files_deleted,
            'total_changes': lines_added + lines_removed
        }
    
    async def _run_git_command(self, cmd: List[str]) -> str:
        """
        Run a Git command asynchronously.
        
        Args:
            cmd: Git command as list of strings
            
        Returns:
            str: Command output
        """
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"Git command failed: {error_msg}")
            
            return stdout.decode()
            
        except Exception as e:
            self.logger.error(f"Error running git command {cmd}: {e}")
            raise
    
    async def _get_files_changed(self, commit_hash: str) -> List[str]:
        """
        Get files changed in a commit.
        
        Args:
            commit_hash: Git commit hash
            
        Returns:
            List[str]: List of changed files
        """
        try:
            cmd = ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash]
            result = await self._run_git_command(cmd)
            return [line.strip() for line in result.split('\n') if line.strip()]
        except Exception as e:
            self.logger.error(f"Error getting files changed for {commit_hash}: {e}")
            return []
    
    async def get_comprehensive_commit_analysis(self, commit_hash: str) -> Dict[str, Any]:
        """
        Get comprehensive analysis of a commit including impact assessment.
        
        Args:
            commit_hash: Git commit hash
            
        Returns:
            Dict containing comprehensive commit analysis
        """
        try:
            # Get basic commit info
            commit_info = await self.get_commit_info(commit_hash)
            
            # Get detailed diff
            diff_output = await self.get_commit_diff(commit_hash)
            
            # Analyze code changes
            code_changes = await self._analyze_code_changes(diff_output)
            
            # Assess impact
            impact_assessment = self._assess_commit_impact(commit_info, code_changes)
            
            # Generate test recommendations
            test_recommendations = self._generate_test_recommendations(code_changes)
            
            return {
                'commit': {
                    'hash': commit_info.hash,
                    'message': commit_info.message,
                    'author': commit_info.author,
                    'date': commit_info.date
                },
                'files_changed': commit_info.files_changed,
                'code_changes': [change.__dict__ for change in code_changes],
                'impact_assessment': impact_assessment,
                'test_recommendations': test_recommendations,
                'risk_level': impact_assessment.get('overall_risk', 'medium'),
                'business_impact': impact_assessment.get('business_impact', 'medium')
            }
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive commit analysis for {commit_hash}: {e}")
            raise
    
    async def get_repository_info(self) -> GitRepository:
        """
        Get comprehensive repository information.
        
        Returns:
            GitRepository: Repository information
        """
        try:
            # Get remote URLs
            remotes = await self._get_remotes()
            
            # Get current branch
            current_branch = await self._get_current_branch()
            
            # Get all branches
            branches = await self._get_all_branches()
            
            # Get last commit
            last_commit = await self._get_last_commit()
            
            return GitRepository(
                url=remotes.get('origin', ''),
                current_branch=current_branch,
                branches=branches,
                remotes=remotes,
                last_commit=last_commit
            )
            
        except Exception as e:
            self.logger.error(f"Error getting repository info: {e}")
            raise
    
    async def get_recent_commits(self, count: int = 10, branch: str = None) -> List[GitCommit]:
        """
        Get recent commits from the repository.
        
        Args:
            count: Number of commits to retrieve
            branch: Branch to get commits from (defaults to current branch)
            
        Returns:
            List[GitCommit]: Recent commits
        """
        try:
            cmd = [
                "git", "log", 
                "--format=%H|%s|%an|%ad", 
                "--date=iso",
                f"-{count}"
            ]
            
            if branch:
                cmd.append(branch)
            
            result = await self._run_git_command(cmd)
            
            commits = []
            for line in result.strip().split('\n'):
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 4:
                        hash_val, message, author, date = parts[:4]
                        files_changed = await self._get_files_changed(hash_val)
                        
                        commits.append(GitCommit(
                            hash=hash_val,
                            message=message,
                            author=author,
                            date=date,
                            files_changed=files_changed
                        ))
            
            return commits
            
        except Exception as e:
            self.logger.error(f"Error getting recent commits: {e}")
            raise
    
    async def compare_branches(self, base_branch: str, compare_branch: str) -> Dict[str, Any]:
        """
        Compare two branches and analyze differences.
        
        Args:
            base_branch: Base branch name
            compare_branch: Branch to compare against
            
        Returns:
            Dict containing branch comparison analysis
        """
        try:
            # Get commits that are different between branches
            cmd = ["git", "rev-list", "--count", f"{base_branch}..{compare_branch}"]
            ahead_count = int((await self._run_git_command(cmd)).strip())
            
            cmd = ["git", "rev-list", "--count", f"{compare_branch}..{base_branch}"]
            behind_count = int((await self._run_git_command(cmd)).strip())
            
            # Get different files
            cmd = ["git", "diff", "--name-only", base_branch, compare_branch]
            different_files = (await self._run_git_command(cmd)).strip().split('\n')
            different_files = [f for f in different_files if f.strip()]
            
            # Get commits in compare_branch but not in base_branch
            cmd = ["git", "log", "--format=%H|%s|%an|%ad", "--date=iso", f"{base_branch}..{compare_branch}"]
            new_commits_output = await self._run_git_command(cmd)
            
            new_commits = []
            for line in new_commits_output.strip().split('\n'):
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 4:
                        hash_val, message, author, date = parts[:4]
                        files_changed = await self._get_files_changed(hash_val)
                        
                        new_commits.append(GitCommit(
                            hash=hash_val,
                            message=message,
                            author=author,
                            date=date,
                            files_changed=files_changed
                        ))
            
            return {
                'base_branch': base_branch,
                'compare_branch': compare_branch,
                'ahead_count': ahead_count,
                'behind_count': behind_count,
                'different_files': different_files,
                'new_commits': [commit.__dict__ for commit in new_commits],
                'has_conflicts': behind_count > 0
            }
            
        except Exception as e:
            self.logger.error(f"Error comparing branches {base_branch} and {compare_branch}: {e}")
            raise
    
    async def _analyze_code_changes(self, diff_output: str) -> List[CodeChange]:
        """Analyze code changes from diff output."""
        changes = []
        current_file = None
        current_change = None
        
        for line in diff_output.split('\n'):
            if line.startswith('diff --git'):
                # Save previous change if exists
                if current_change:
                    changes.append(current_change)
                
                # Start new file analysis
                parts = line.split()
                if len(parts) > 3:
                    current_file = parts[-1]
                    current_change = CodeChange(
                        file_path=current_file,
                        change_type='modified',
                        lines_added=0,
                        lines_removed=0,
                        complexity_change=0,
                        affected_modules=[],
                        business_impact='low',
                        risk_level='low',
                        test_impact=[]
                    )
            elif line.startswith('new file mode'):
                if current_change:
                    current_change.change_type = 'added'
            elif line.startswith('deleted file mode'):
                if current_change:
                    current_change.change_type = 'deleted'
            elif line.startswith('+') and not line.startswith('+++'):
                if current_change:
                    current_change.lines_added += 1
            elif line.startswith('-') and not line.startswith('---'):
                if current_change:
                    current_change.lines_removed += 1
        
        # Save last change
        if current_change:
            changes.append(current_change)
        
        # Analyze each change
        for change in changes:
            change.affected_modules = self._identify_affected_modules(change.file_path)
            change.business_impact = self._assess_business_impact(change)
            change.risk_level = self._assess_risk_level(change)
            change.test_impact = self._generate_test_impact(change)
            change.complexity_change = self._assess_complexity_change(change)
        
        return changes
    
    def _identify_affected_modules(self, file_path: str) -> List[str]:
        """Identify which modules are affected by a file change."""
        affected_modules = []
        
        for module, patterns in self.module_patterns.items():
            for pattern in patterns:
                if pattern in file_path:
                    affected_modules.append(module)
                    break
        
        # If no specific module found, try to infer from file extension or path
        if not affected_modules:
            if file_path.endswith(('.py', '.js', '.ts', '.java', '.go')):
                affected_modules.append('code')
            elif file_path.endswith(('.yml', '.yaml', '.json', '.xml', '.toml')):
                affected_modules.append('config')
            elif file_path.endswith(('.md', '.txt', '.rst')):
                affected_modules.append('documentation')
        
        return affected_modules or ['unknown']
    
    def _assess_business_impact(self, change: CodeChange) -> str:
        """Assess business impact of a code change."""
        impact_score = 0
        
        # File type impact
        if any(module in change.affected_modules for module in ['api', 'services']):
            impact_score += 3
        elif any(module in change.affected_modules for module in ['ui', 'database']):
            impact_score += 2
        elif any(module in change.affected_modules for module in ['config', 'utils']):
            impact_score += 1
        
        # Change size impact
        total_changes = change.lines_added + change.lines_removed
        if total_changes > 100:
            impact_score += 2
        elif total_changes > 50:
            impact_score += 1
        
        # Change type impact
        if change.change_type == 'added':
            impact_score += 1
        elif change.change_type == 'deleted':
            impact_score += 2
        
        if impact_score >= 4:
            return 'high'
        elif impact_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _assess_risk_level(self, change: CodeChange) -> str:
        """Assess risk level of a code change."""
        risk_score = 0
        
        # Critical modules
        if any(module in change.affected_modules for module in ['api', 'database']):
            risk_score += 2
        elif any(module in change.affected_modules for module in ['services', 'config']):
            risk_score += 1
        
        # Change size
        total_changes = change.lines_added + change.lines_removed
        if total_changes > 200:
            risk_score += 2
        elif total_changes > 100:
            risk_score += 1
        
        # Change type
        if change.change_type == 'deleted':
            risk_score += 2
        elif change.change_type == 'added':
            risk_score += 1
        
        if risk_score >= 4:
            return 'high'
        elif risk_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _generate_test_impact(self, change: CodeChange) -> List[str]:
        """Generate test impact recommendations."""
        test_impacts = []
        
        # Module-based test recommendations
        if 'api' in change.affected_modules:
            test_impacts.extend(['api_tests', 'integration_tests'])
        if 'ui' in change.affected_modules:
            test_impacts.extend(['ui_tests', 'e2e_tests'])
        if 'database' in change.affected_modules:
            test_impacts.extend(['database_tests', 'migration_tests'])
        if 'services' in change.affected_modules:
            test_impacts.extend(['unit_tests', 'service_tests'])
        
        # Change type-based recommendations
        if change.change_type == 'added':
            test_impacts.append('new_feature_tests')
        elif change.change_type == 'deleted':
            test_impacts.append('regression_tests')
        
        # Risk-based recommendations
        if change.risk_level == 'high':
            test_impacts.extend(['critical_path_tests', 'smoke_tests'])
        
        return list(set(test_impacts))  # Remove duplicates
    
    def _assess_complexity_change(self, change: CodeChange) -> int:
        """Assess complexity change of a code change."""
        complexity = 0
        
        # Lines changed
        total_changes = change.lines_added + change.lines_removed
        complexity += min(total_changes // 10, 5)
        
        # Module complexity
        if 'api' in change.affected_modules:
            complexity += 2
        if 'database' in change.affected_modules:
            complexity += 2
        if 'services' in change.affected_modules:
            complexity += 1
        
        return min(complexity, 10)
    
    def _assess_commit_impact(self, commit: GitCommit, changes: List[CodeChange]) -> Dict[str, Any]:
        """Assess overall impact of a commit."""
        total_lines_changed = sum(change.lines_added + change.lines_removed for change in changes)
        affected_modules = set()
        for change in changes:
            affected_modules.update(change.affected_modules)
        
        # Determine overall risk level
        high_risk_changes = [c for c in changes if c.risk_level == 'high']
        medium_risk_changes = [c for c in changes if c.risk_level == 'medium']
        
        if len(high_risk_changes) > 0 or total_lines_changed > 200:
            overall_risk = 'high'
        elif len(medium_risk_changes) > 1 or total_lines_changed > 100:
            overall_risk = 'medium'
        else:
            overall_risk = 'low'
        
        # Determine business impact
        high_impact_changes = [c for c in changes if c.business_impact == 'high']
        medium_impact_changes = [c for c in changes if c.business_impact == 'medium']
        
        if len(high_impact_changes) > 0:
            business_impact = 'high'
        elif len(medium_impact_changes) > 0 or len(affected_modules) > 2:
            business_impact = 'medium'
        else:
            business_impact = 'low'
        
        return {
            'overall_risk': overall_risk,
            'business_impact': business_impact,
            'total_lines_changed': total_lines_changed,
            'affected_modules': list(affected_modules),
            'change_count': len(changes),
            'high_risk_changes': len(high_risk_changes),
            'medium_risk_changes': len(medium_risk_changes),
            'complexity_score': sum(change.complexity_change for change in changes)
        }
    
    def _generate_test_recommendations(self, changes: List[CodeChange]) -> Dict[str, Any]:
        """Generate comprehensive test recommendations."""
        all_test_impacts = []
        for change in changes:
            all_test_impacts.extend(change.test_impact)
        
        # Count test impact frequency
        test_counts = {}
        for test_type in all_test_impacts:
            test_counts[test_type] = test_counts.get(test_type, 0) + 1
        
        # Prioritize test recommendations
        prioritized_tests = sorted(test_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'recommended_tests': [test for test, count in prioritized_tests],
            'test_priorities': {
                'critical': [test for test, count in prioritized_tests if count >= 3],
                'high': [test for test, count in prioritized_tests if count == 2],
                'medium': [test for test, count in prioritized_tests if count == 1]
            },
            'estimated_test_time': len(all_test_impacts) * 5,  # 5 minutes per test type
            'coverage_areas': list(set(all_test_impacts))
        }
    
    async def _get_remotes(self) -> Dict[str, str]:
        """Get remote repository URLs."""
        try:
            cmd = ["git", "remote", "-v"]
            result = await self._run_git_command(cmd)
            
            remotes = {}
            for line in result.strip().split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        remote_name = parts[0]
                        remote_url = parts[1]
                        remotes[remote_name] = remote_url
            
            return remotes
        except Exception as e:
            self.logger.error(f"Error getting remotes: {e}")
            return {}
    
    async def _get_current_branch(self) -> str:
        """Get current branch name."""
        try:
            cmd = ["git", "branch", "--show-current"]
            return (await self._run_git_command(cmd)).strip()
        except Exception as e:
            self.logger.error(f"Error getting current branch: {e}")
            return "unknown"
    
    async def _get_all_branches(self) -> List[GitBranch]:
        """Get all branches with detailed information."""
        try:
            cmd = ["git", "branch", "-v"]
            result = await self._run_git_command(cmd)
            
            branches = []
            for line in result.strip().split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        is_current = line.startswith('*')
                        branch_name = parts[0].lstrip('*')
                        last_commit_hash = parts[1]
                        last_commit_message = ' '.join(parts[2:])
                        
                        # Get additional commit info
                        commit_info = await self.get_commit_info(last_commit_hash)
                        
                        branches.append(GitBranch(
                            name=branch_name,
                            is_current=is_current,
                            last_commit_hash=last_commit_hash,
                            last_commit_message=last_commit_message,
                            last_commit_author=commit_info.author,
                            last_commit_date=commit_info.date
                        ))
            
            return branches
        except Exception as e:
            self.logger.error(f"Error getting branches: {e}")
            return []
    
    async def _get_last_commit(self) -> Optional[GitCommit]:
        """Get the last commit."""
        try:
            return await self.get_commit_info("HEAD")
        except Exception as e:
            self.logger.error(f"Error getting last commit: {e}")
            return None
