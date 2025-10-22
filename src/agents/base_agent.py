"""
Base Agent class for the Smarter Case system.
Provides common functionality for all specialized agents.
"""
import asyncio
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import aisuite as ai

from ..models.agent_models import (
    AgentStatus, AgentType, AgentContext, AgentResult, 
    AgentMessage, AgentConfig, WorkflowContext
)
from ..utils.logger import get_logger


@dataclass
class AgentCapabilities:
    """Defines what capabilities an agent has."""
    can_analyze_code: bool = False
    can_analyze_requirements: bool = False
    can_select_tests: bool = False
    can_reflect: bool = False
    can_evaluate: bool = False
    can_execute: bool = False
    can_use_tools: bool = False
    can_make_llm_calls: bool = True


class BaseAgent(ABC):
    """
    Base class for all agents in the Smarter Case system.
    
    This class provides common functionality including:
    - LLM client management
    - Message handling
    - Status tracking
    - Error handling and retry logic
    - Logging and metrics
    """
    
    def __init__(
        self, 
        agent_id: str,
        agent_type: AgentType,
        config: AgentConfig,
        capabilities: AgentCapabilities
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.config = config
        self.capabilities = capabilities
        
        # Initialize AI client
        self.ai_client = ai.Client()
        
        # Initialize logger
        self.logger = get_logger(f"agent.{agent_id}")
        
        # Agent state
        self.context: Optional[AgentContext] = None
        self.status = AgentStatus.IDLE
        self.last_result: Optional[AgentResult] = None
        
        # Message handling
        self.message_queue: List[AgentMessage] = []
        self.message_handlers: Dict[str, callable] = {}
        
        # Metrics
        self.execution_count = 0
        self.total_execution_time = 0.0
        self.success_count = 0
        self.failure_count = 0
        
        self.logger.info(f"Initialized {agent_type.value} agent: {agent_id}")
    
    async def execute(
        self, 
        input_data: Dict[str, Any], 
        workflow_context: WorkflowContext
    ) -> AgentResult:
        """
        Execute the agent's main functionality.
        
        Args:
            input_data: Input data for the agent
            workflow_context: Context of the entire workflow
            
        Returns:
            AgentResult: Result of the agent execution
        """
        start_time = time.time()
        self.status = AgentStatus.RUNNING
        
        # Create agent context
        self.context = AgentContext(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            status=self.status,
            start_time=start_time
        )
        
        self.logger.info(f"Starting execution for agent {self.agent_id}")
        
        try:
            # Execute the agent's specific logic
            result_data = await self._execute_impl(input_data, workflow_context)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Create successful result
            self.last_result = AgentResult(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                result_data=result_data,
                execution_time=execution_time,
                confidence_score=self._calculate_confidence_score(result_data),
                metadata=self._get_execution_metadata()
            )
            
            # Update metrics
            self._update_metrics(execution_time, success=True)
            
            self.logger.info(
                f"Agent {self.agent_id} completed successfully in {execution_time:.2f}s"
            )
            
            return self.last_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_message = str(e)
            
            self.logger.error(
                f"Agent {self.agent_id} failed after {execution_time:.2f}s: {error_message}"
            )
            
            # Create failed result
            self.last_result = AgentResult(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status=AgentStatus.FAILED,
                result_data={},
                execution_time=execution_time,
                error_message=error_message,
                metadata=self._get_execution_metadata()
            )
            
            # Update metrics
            self._update_metrics(execution_time, success=False)
            
            return self.last_result
            
        finally:
            self.status = AgentStatus.IDLE
            if self.context:
                self.context.status = self.status
                self.context.end_time = time.time()
    
    @abstractmethod
    async def _execute_impl(
        self, 
        input_data: Dict[str, Any], 
        workflow_context: WorkflowContext
    ) -> Dict[str, Any]:
        """
        Implement the specific logic for this agent.
        
        Args:
            input_data: Input data for the agent
            workflow_context: Context of the entire workflow
            
        Returns:
            Dict[str, Any]: Result data from the agent execution
        """
        pass
    
    async def send_message(
        self, 
        receiver: str, 
        message_type: str, 
        payload: Dict[str, Any],
        correlation_id: str = ""
    ) -> None:
        """Send a message to another agent."""
        message = AgentMessage(
            sender=self.agent_id,
            receiver=receiver,
            message_type=message_type,
            payload=payload,
            correlation_id=correlation_id
        )
        
        self.logger.debug(
            f"Sending message to {receiver}: {message_type}"
        )
        
        # In a real implementation, this would go through a message bus
        # For now, we'll just log it
        self.message_queue.append(message)
    
    async def receive_message(self, message: AgentMessage) -> None:
        """Receive and handle a message from another agent."""
        self.logger.debug(
            f"Received message from {message.sender}: {message.message_type}"
        )
        
        # Handle the message if we have a handler for it
        if message.message_type in self.message_handlers:
            try:
                await self.message_handlers[message.message_type](message)
            except Exception as e:
                self.logger.error(
                    f"Error handling message {message.message_type}: {e}"
                )
        else:
            self.logger.warning(
                f"No handler for message type: {message.message_type}"
            )
    
    def register_message_handler(self, message_type: str, handler: callable) -> None:
        """Register a handler for a specific message type."""
        self.message_handlers[message_type] = handler
        self.logger.debug(f"Registered handler for message type: {message_type}")
    
    async def make_llm_call(
        self, 
        prompt: str, 
        model: str = "openai:gpt-4o",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List] = None
    ) -> str:
        """
        Make a call to the LLM using aisuite.
        
        Args:
            prompt: The prompt to send to the LLM
            model: The model to use (default: openai:gpt-4o)
            temperature: Temperature for response generation
            max_tokens: Maximum tokens in response
            tools: Optional tools for the LLM to use
            
        Returns:
            str: Response from the LLM
        """
        if not self.capabilities.can_make_llm_calls:
            raise ValueError(f"Agent {self.agent_id} cannot make LLM calls")
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            response = self.ai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise
    
    def _calculate_confidence_score(self, result_data: Dict[str, Any]) -> Optional[float]:
        """
        Calculate confidence score for the agent's result.
        Override in subclasses for specific confidence calculation.
        """
        return None
    
    def _get_execution_metadata(self) -> Dict[str, Any]:
        """Get metadata about the agent's execution."""
        return {
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "average_execution_time": (
                self.total_execution_time / self.execution_count 
                if self.execution_count > 0 else 0
            )
        }
    
    def _update_metrics(self, execution_time: float, success: bool) -> None:
        """Update agent metrics."""
        self.execution_count += 1
        self.total_execution_time += execution_time
        
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current agent metrics."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": (
                self.success_count / self.execution_count 
                if self.execution_count > 0 else 0
            ),
            "average_execution_time": (
                self.total_execution_time / self.execution_count 
                if self.execution_count > 0 else 0
            ),
            "status": self.status.value
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.agent_id}, type={self.agent_type.value})"
