"""
Code Analysis Agent for analyzing Git changes and identifying impact scope.
"""
import asyncio
import subprocess
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .base_agent import BaseAgent, AgentCapabilities
from ..models.agent_models import AgentType, AgentConfig, WorkflowContext
from ..tools.git_tools import GitAnalyzer
from ..utils.logger import get_logger


@dataclass
class CodeChange:
    """Represents a code change."""
    file_path: str
    change_type: str  # added, modified, deleted
    lines_changed: int
    impact_modules: List[str]
    business_domains: List[str]


@dataclass
class CodeAnalysisResult:
    """Result of code analysis."""
    commit_hash: str
    branch: str
    changes: List[CodeChange]
    affected_modules: List[str]
    business_impact: List[str]
    confidence_score: float


class CodeAnalysisAgent(BaseAgent):
    """
    Agent responsible for analyzing Git code changes and identifying impact scope.
    
    This agent:
    1. Analyzes Git commits to identify changed files
    2. Determines the type of changes (added, modified, deleted)
    3. Identifies affected modules and business domains
    4. Calculates impact scope and confidence
    """
    
    def __init__(self, agent_id: str = "code_analysis_agent", config: Optional[AgentConfig] = None):
        # Set up capabilities
        capabilities = AgentCapabilities(
            can_analyze_code=True,
            can_make_llm_calls=True
        )
        
        # Default config
        if config is None:
            config = AgentConfig(
                agent_id=agent_id,
                agent_type=AgentType.CODE_ANALYSIS,
                timeout=300,
                max_retries=3
            )
        
        super().__init__(agent_id, AgentType.CODE_ANALYSIS, config, capabilities)
        
        # Initialize tools
        self.git_analyzer = GitAnalyzer()
        
        # Register message handlers
        self.register_message_handler("analyze_commit", self._handle_analyze_commit)
        
        self.logger.info(f"Code Analysis Agent {agent_id} initialized")
    
    async def _execute_impl(
        self, 
        input_data: Dict[str, Any], 
        workflow_context: WorkflowContext
    ) -> Dict[str, Any]:
        """
        Execute code analysis.
        
        Args:
            input_data: Should contain 'commit_hash' and 'branch'
            workflow_context: Workflow context
            
        Returns:
            Dict containing analysis results
        """
        commit_hash = input_data.get('commit_hash')
        branch = input_data.get('branch', 'main')
        
        if not commit_hash:
            raise ValueError("commit_hash is required for code analysis")
        
        self.logger.info(f"Analyzing commit {commit_hash} on branch {branch}")
        
        # Analyze the commit
        analysis_result = await self._analyze_commit(commit_hash, branch)
        
        return {
            "commit_hash": commit_hash,
            "branch": branch,
            "changes": [
                {
                    "file_path": change.file_path,
                    "change_type": change.change_type,
                    "lines_changed": change.lines_changed,
                    "impact_modules": change.impact_modules,
                    "business_domains": change.business_domains
                }
                for change in analysis_result.changes
            ],
            "affected_modules": analysis_result.affected_modules,
            "business_impact": analysis_result.business_impact,
            "confidence_score": analysis_result.confidence_score,
            "analysis_metadata": {
                "total_files_changed": len(analysis_result.changes),
                "total_modules_affected": len(analysis_result.affected_modules),
                "analysis_timestamp": self.context.start_time if self.context else None
            }
        }
    
    async def _analyze_commit(self, commit_hash: str, branch: str) -> CodeAnalysisResult:
        """
        Analyze a specific commit for code changes and impact.
        
        Args:
            commit_hash: Git commit hash
            branch: Git branch name
            
        Returns:
            CodeAnalysisResult: Analysis results
        """
        try:
            # Get commit diff
            diff_output = await self.git_analyzer.get_commit_diff(commit_hash)
            
            # Parse the diff to identify changes
            changes = await self._parse_diff(diff_output)
            
            # Analyze impact of changes
            affected_modules = await self._analyze_impact(changes)
            
            # Identify business domains affected
            business_impact = await self._identify_business_domains(changes)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence(changes, affected_modules)
            
            return CodeAnalysisResult(
                commit_hash=commit_hash,
                branch=branch,
                changes=changes,
                affected_modules=affected_modules,
                business_impact=business_impact,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing commit {commit_hash}: {e}")
            raise
    
    async def _parse_diff(self, diff_output: str) -> List[CodeChange]:
        """
        Parse Git diff output to identify changes.
        
        Args:
            diff_output: Raw diff output from Git
            
        Returns:
            List[CodeChange]: Parsed changes
        """
        changes = []
        current_file = None
        current_change_type = None
        
        for line in diff_output.split('\n'):
            if line.startswith('diff --git'):
                # Extract file path
                parts = line.split()
                if len(parts) >= 4:
                    current_file = parts[3][2:]  # Remove 'b/' prefix
            elif line.startswith('new file mode'):
                current_change_type = 'added'
            elif line.startswith('deleted file mode'):
                current_change_type = 'deleted'
            elif line.startswith('index') and current_change_type is None:
                current_change_type = 'modified'
            elif line.startswith('@@') and current_file and current_change_type:
                # Count lines changed (simplified)
                lines_changed = self._count_lines_changed(line)
                
                # Determine impact modules
                impact_modules = self._determine_impact_modules(current_file)
                
                # Determine business domains
                business_domains = self._determine_business_domains(current_file)
                
                changes.append(CodeChange(
                    file_path=current_file,
                    change_type=current_change_type,
                    lines_changed=lines_changed,
                    impact_modules=impact_modules,
                    business_domains=business_domains
                ))
        
        return changes
    
    def _count_lines_changed(self, hunk_header: str) -> int:
        """Count lines changed in a diff hunk."""
        try:
            # Extract numbers from @@ -a,b +c,d @@ format
            parts = hunk_header.split()
            if len(parts) >= 3:
                old_part = parts[1].split(',')
                new_part = parts[2].split(',')
                
                old_lines = int(old_part[1]) if len(old_part) > 1 else 1
                new_lines = int(new_part[1]) if len(new_part) > 1 else 1
                
                return abs(new_lines - old_lines)
        except (ValueError, IndexError):
            pass
        
        return 0
    
    def _determine_impact_modules(self, file_path: str) -> List[str]:
        """
        Determine which modules are impacted by a file change.
        
        Args:
            file_path: Path to the changed file
            
        Returns:
            List[str]: Affected modules
        """
        modules = []
        
        # Simple heuristic based on file path
        if file_path.startswith('src/api/'):
            modules.append('api')
        elif file_path.startswith('src/ui/'):
            modules.append('ui')
        elif file_path.startswith('src/models/'):
            modules.append('models')
        elif file_path.startswith('src/services/'):
            modules.append('services')
        elif file_path.startswith('tests/api/'):
            modules.append('api_tests')
        elif file_path.startswith('tests/ui/'):
            modules.append('ui_tests')
        
        # If no specific module found, use directory name
        if not modules:
            path_parts = file_path.split('/')
            if len(path_parts) > 1:
                modules.append(path_parts[1])
        
        return modules
    
    def _determine_business_domains(self, file_path: str) -> List[str]:
        """
        Determine which business domains are affected by a file change.
        
        Args:
            file_path: Path to the changed file
            
        Returns:
            List[str]: Affected business domains
        """
        domains = []
        
        # Simple heuristic based on file path
        if 'user' in file_path.lower():
            domains.append('user_management')
        elif 'auth' in file_path.lower():
            domains.append('authentication')
        elif 'payment' in file_path.lower():
            domains.append('payment')
        elif 'order' in file_path.lower():
            domains.append('order_management')
        elif 'product' in file_path.lower():
            domains.append('product_catalog')
        
        # Default domain if none found
        if not domains:
            domains.append('general')
        
        return domains
    
    async def _analyze_impact(self, changes: List[CodeChange]) -> List[str]:
        """
        Analyze the overall impact of changes.
        
        Args:
            changes: List of code changes
            
        Returns:
            List[str]: Affected modules
        """
        affected_modules = set()
        
        for change in changes:
            affected_modules.update(change.impact_modules)
        
        return list(affected_modules)
    
    async def _identify_business_domains(self, changes: List[CodeChange]) -> List[str]:
        """
        Identify business domains affected by changes.
        
        Args:
            changes: List of code changes
            
        Returns:
            List[str]: Affected business domains
        """
        business_domains = set()
        
        for change in changes:
            business_domains.update(change.business_domains)
        
        return list(business_domains)
    
    def _calculate_confidence(self, changes: List[CodeChange], affected_modules: List[str]) -> float:
        """
        Calculate confidence score for the analysis.
        
        Args:
            changes: List of code changes
            affected_modules: List of affected modules
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        # Simple confidence calculation based on number of changes and modules
        total_changes = len(changes)
        total_modules = len(affected_modules)
        
        # Higher confidence with fewer changes (more focused impact)
        change_confidence = min(1.0, 10.0 / max(1, total_changes))
        
        # Higher confidence with fewer affected modules
        module_confidence = min(1.0, 5.0 / max(1, total_modules))
        
        # Average the confidence scores
        return (change_confidence + module_confidence) / 2.0
    
    async def _handle_analyze_commit(self, message) -> None:
        """Handle analyze_commit message."""
        self.logger.info(f"Handling analyze_commit message: {message.payload}")
        # Implementation would depend on the message structure and requirements
