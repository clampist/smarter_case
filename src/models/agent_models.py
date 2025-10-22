"""
Agent-related data models for the Smarter Case system.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import time


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(Enum):
    """Types of agents in the system."""
    CODE_ANALYSIS = "code_analysis"
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    TEST_SELECTION = "test_selection"
    REFLECTION = "reflection"
    EVALUATION = "evaluation"
    EXECUTION = "execution"


@dataclass
class AgentMessage:
    """Message structure for agent communication."""
    sender: str
    receiver: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    correlation_id: str = ""
    reply_to: Optional[str] = None


@dataclass
class AgentContext:
    """Context information for agent execution."""
    agent_id: str
    agent_type: AgentType
    status: AgentStatus = AgentStatus.IDLE
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result structure for agent execution."""
    agent_id: str
    agent_type: AgentType
    status: AgentStatus
    result_data: Dict[str, Any]
    execution_time: float
    confidence_score: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowContext:
    """Context for the entire workflow execution."""
    workflow_id: str
    trigger_event: Dict[str, Any]
    shared_data: Dict[str, Any] = field(default_factory=dict)
    execution_state: Dict[str, AgentStatus] = field(default_factory=dict)
    results: Dict[str, AgentResult] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None


@dataclass
class AgentConfig:
    """Configuration for agent behavior."""
    agent_id: str
    agent_type: AgentType
    timeout: int = 300
    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_factor: float = 2.0
    model_config: Dict[str, Any] = field(default_factory=dict)
    tool_config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
