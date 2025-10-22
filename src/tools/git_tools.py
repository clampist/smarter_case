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


class GitAnalyzer:
    """
    Git analysis tools for the Smarter Case system.
    
    This class provides functionality to:
    - Analyze Git commits and changes
    - Get repository information
    - Extract diff information
    - Identify affected files and modules
    """
    
    def __init__(self):
        self.logger = get_logger("git_analyzer")
    
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
