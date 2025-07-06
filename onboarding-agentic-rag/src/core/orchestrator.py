"""
Agent Orchestrator Implementation
Coordinates multiple agents and manages response synthesis for Agentic RAG
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import structlog
import time

from langchain.schema import Document
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

from ..agents.base_agent import AgentContext, AgentResponse, agent_registry
from ..core.vector_service import VectorService
from ..core.config import settings

logger = structlog.get_logger(__name__)

@dataclass
class OrchestrationResult:
    """Result from agent orchestration"""
    final_response: str
    agent_responses: List[AgentResponse]
    confidence: float
    sources: List[Document]
    metadata: Dict[str, Any]
    processing_time: float
    agent_sequence: List[str]

class AgentOrchestrator:
    """Orchestrates multiple agents for complex query processing"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.1,
            max_tokens=1500
        )
        self.vector_service = VectorService()
        
        # Setup response synthesis prompt
        self._setup_prompts()
        
        # Orchestration metrics
        self.total_orchestrations = 0
        self.successful_orchestrations = 0
        self.average_processing_time = 0.0
    
    def _setup_prompts(self):
        """Setup prompt templates for orchestration"""
        
        # Response synthesis prompt
        self.synthesis_prompt = ChatPromptTemplate.from_template("""
        You are an intelligent assistant coordinating multiple specialized agents to provide comprehensive answers.
        
        User Query: {query}
        
        Agent Responses:
        {agent_responses}
        
        User Context: {user_context}
        
        Instructions:
        1. Synthesize a comprehensive response that addresses all aspects of the query
        2. Eliminate redundancy and contradictions
        3. Maintain a coherent narrative flow
        4. Include relevant information from all contributing agents
        5. Ensure the response is personalized to the user's context
        6. Provide actionable next steps when appropriate
        
        Synthesized Response:
        """)
        
        # Quality assessment prompt
        self.quality_prompt = ChatPromptTemplate.from_template("""
        Assess the quality of the synthesized response:
        
        Query: {query}
        Response: {response}
        Agent Contributions: {agent_contributions}
        
        Rate the response on a scale of 0.0 to 1.0 for:
        - Completeness: Does it address all aspects of the query?
        - Accuracy: Is the information correct and up-to-date?
        - Relevance: Is it relevant to the user's context?
        - Clarity: Is it clear and well-structured?
        
        Return only the average score (0.0-1.0).
        """)
    
    async def orchestrate_query(self, context: AgentContext) -> OrchestrationResult:
        """Orchestrate multiple agents to process a query"""
        
        start_time = time.time()
        self.total_orchestrations += 1
        
        try:
            logger.info("Starting query orchestration", 
                       query=context.query,
                       user_id=context.user_id)
            
            # Step 1: Route query to appropriate agents
            agent_assignments = await self._route_to_agents(context)
            
            # Step 2: Execute agents in parallel
            agent_responses = await self._execute_agents(agent_assignments, context)
            
            # Step 3: Synthesize responses
            final_response = await self._synthesize_responses(
                context.query, 
                agent_responses, 
                context
            )
            
            # Step 4: Assess quality
            confidence = await self._assess_quality(
                context.query, 
                final_response, 
                agent_responses
            )
            
            # Step 5: Extract sources
            sources = self._extract_sources(agent_responses)
            
            # Step 6: Generate metadata
            metadata = self._generate_metadata(agent_responses, context)
            
            processing_time = time.time() - start_time
            self._update_metrics(processing_time, True)
            
            result = OrchestrationResult(
                final_response=final_response,
                agent_responses=agent_responses,
                confidence=confidence,
                sources=sources,
                metadata=metadata,
                processing_time=processing_time,
                agent_sequence=[resp.metadata.get("agent_role", "unknown") 
                              for resp in agent_responses]
            )
            
            logger.info("Orchestration completed",
                       processing_time=processing_time,
                       agent_count=len(agent_responses),
                       confidence=confidence)
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_metrics(processing_time, False)
            
            logger.error("Orchestration failed", error=str(e))
            
            # Return error result
            return OrchestrationResult(
                final_response=f"I encountered an error while processing your request: {str(e)}",
                agent_responses=[],
                confidence=0.0,
                sources=[],
                metadata={"error": str(e)},
                processing_time=processing_time,
                agent_sequence=[]
            )
    
    async def _route_to_agents(self, context: AgentContext) -> List[Tuple[Any, float]]:
        """Route query to appropriate agents with priorities"""
        return await agent_registry.route_query(context.query, context)
    
    async def _execute_agents(self, agent_assignments: List[Tuple[Any, float]], 
                             context: AgentContext) -> List[AgentResponse]:
        """Execute agents in parallel"""
        
        # Create tasks for parallel execution
        tasks = []
        for agent, priority in agent_assignments:
            task = asyncio.create_task(agent.execute(context))
            tasks.append((task, priority))
        
        # Execute all tasks
        results = await asyncio.gather(*[task for task, _ in tasks])
        
        # Filter out failed responses and sort by priority
        successful_responses = []
        for (task, priority), response in zip(tasks, results):
            if response.confidence > 0.0:  # Filter out error responses
                response.metadata["priority"] = priority
                response.metadata["agent_role"] = task.get_name() if hasattr(task, 'get_name') else "unknown"
                successful_responses.append(response)
        
        # Sort by priority (highest first)
        successful_responses.sort(key=lambda x: x.metadata.get("priority", 0), reverse=True)
        
        logger.info("Agent execution completed",
                   total_agents=len(agent_assignments),
                   successful_agents=len(successful_responses))
        
        return successful_responses
    
    async def _synthesize_responses(self, query: str, agent_responses: List[AgentResponse], 
                                   context: AgentContext) -> str:
        """Synthesize multiple agent responses into a coherent response"""
        
        if not agent_responses:
            return "I'm unable to provide a comprehensive answer at this time."
        
        if len(agent_responses) == 1:
            return agent_responses[0].content
        
        # Format agent responses for synthesis
        agent_responses_text = []
        for i, response in enumerate(agent_responses):
            agent_responses_text.append(
                f"Agent {i+1} ({response.metadata.get('agent_role', 'unknown')}):\n"
                f"Confidence: {response.confidence:.2f}\n"
                f"Response: {response.content}\n"
            )
        
        # Synthesize using LLM
        chain = self.synthesis_prompt | self.llm | StrOutputParser()
        
        synthesis_result = await chain.ainvoke({
            "query": query,
            "agent_responses": "\n\n".join(agent_responses_text),
            "user_context": str(context.user_profile)
        })
        
        return synthesis_result
    
    async def _assess_quality(self, query: str, response: str, 
                             agent_responses: List[AgentResponse]) -> float:
        """Assess the quality of the synthesized response"""
        
        if not agent_responses:
            return 0.0
        
        # Format agent contributions for quality assessment
        agent_contributions = []
        for response in agent_responses:
            agent_contributions.append(
                f"Agent: {response.metadata.get('agent_role', 'unknown')}, "
                f"Confidence: {response.confidence:.2f}"
            )
        
        # Assess quality using LLM
        chain = self.quality_prompt | self.llm | StrOutputParser()
        
        try:
            quality_score = await chain.ainvoke({
                "query": query,
                "response": response,
                "agent_contributions": "\n".join(agent_contributions)
            })
            
            # Parse score (expecting a float)
            try:
                return float(quality_score.strip())
            except ValueError:
                return 0.5  # Default score if parsing fails
                
        except Exception as e:
            logger.error("Quality assessment failed", error=str(e))
            return 0.5
    
    def _extract_sources(self, agent_responses: List[AgentResponse]) -> List[Document]:
        """Extract and deduplicate sources from agent responses"""
        all_sources = []
        seen_sources = set()
        
        for response in agent_responses:
            for source in response.sources:
                # Create a unique identifier for the source
                source_id = f"{source.page_content[:100]}_{source.metadata.get('source', 'unknown')}"
                
                if source_id not in seen_sources:
                    all_sources.append(source)
                    seen_sources.add(source_id)
        
        return all_sources
    
    def _generate_metadata(self, agent_responses: List[AgentResponse], 
                          context: AgentContext) -> Dict[str, Any]:
        """Generate comprehensive metadata for the orchestration result"""
        
        metadata = {
            "user_id": context.user_id,
            "session_id": context.session_id,
            "agent_count": len(agent_responses),
            "agent_roles": [resp.metadata.get("agent_role", "unknown") 
                           for resp in agent_responses],
            "total_confidence": sum(resp.confidence for resp in agent_responses),
            "average_confidence": sum(resp.confidence for resp in agent_responses) / len(agent_responses) if agent_responses else 0.0,
            "total_processing_time": sum(resp.processing_time for resp in agent_responses),
            "user_profile_keys": list(context.user_profile.keys()),
            "conversation_history_length": len(context.conversation_history)
        }
        
        return metadata
    
    def _update_metrics(self, processing_time: float, success: bool):
        """Update orchestration metrics"""
        if success:
            self.successful_orchestrations += 1
        
        # Update average processing time
        if self.total_orchestrations > 0:
            self.average_processing_time = (
                (self.average_processing_time * (self.total_orchestrations - 1) + processing_time) 
                / self.total_orchestrations
            )
    
    def get_orchestrator_metrics(self) -> Dict[str, Any]:
        """Get orchestrator performance metrics"""
        success_rate = (
            self.successful_orchestrations / self.total_orchestrations 
            if self.total_orchestrations > 0 else 0.0
        )
        
        return {
            "total_orchestrations": self.total_orchestrations,
            "successful_orchestrations": self.successful_orchestrations,
            "success_rate": success_rate,
            "average_processing_time": self.average_processing_time
        }
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return agent_registry.get_registry_status()
    
    async def add_agent_to_conversation(self, agent_role: str, context: AgentContext):
        """Dynamically add an agent to the conversation"""
        # This could be used for dynamic agent creation based on conversation needs
        logger.info("Adding agent to conversation", agent_role=agent_role)
        # Implementation would depend on specific requirements

# Global orchestrator instance
orchestrator = AgentOrchestrator() 