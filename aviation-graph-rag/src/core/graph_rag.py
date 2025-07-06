"""
Graph RAG Core Implementation
Production-ready Graph RAG system for aviation domain
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import structlog

from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Weaviate
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

from .graph_service import GraphService
from .vector_service import VectorService
from .config import settings

logger = structlog.get_logger(__name__)

@dataclass
class QueryContext:
    """Context information for a query"""
    query: str
    intent: str
    entities: List[Dict[str, Any]]
    graph_context: List[Dict[str, Any]]
    vector_context: List[Document]
    user_context: Dict[str, Any]

@dataclass
class GraphRAGResponse:
    """Response from Graph RAG system"""
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    graph_paths: List[Dict[str, Any]]
    vector_sources: List[Document]
    metadata: Dict[str, Any]

class GraphRAGPipeline:
    """Production-ready Graph RAG pipeline for aviation domain"""
    
    def __init__(self):
        self.graph_service = GraphService()
        self.vector_service = VectorService()
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.1,
            max_tokens=1000
        )
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL
        )
        
        # Initialize prompt templates
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Setup prompt templates for different query types"""
        
        # Intent classification prompt
        self.intent_prompt = ChatPromptTemplate.from_template("""
        Classify the following aviation-related query into one of these categories:
        - flight_info: Flight schedules, status, delays, cancellations
        - safety: Safety protocols, regulations, emergency procedures
        - maintenance: Equipment maintenance, repair procedures
        - customer_service: Booking, baggage, boarding assistance
        - technical: Aircraft specifications, systems information
        
        Query: {query}
        
        Respond with only the category name.
        """)
        
        # Entity extraction prompt
        self.entity_prompt = ChatPromptTemplate.from_template("""
        Extract aviation-specific entities from the query:
        - Aircraft types (e.g., Boeing 737, Airbus A320)
        - Flight numbers (e.g., AA123, DL456)
        - Airport codes (e.g., JFK, LAX, ORD)
        - Equipment IDs (e.g., Engine serial numbers)
        - Safety protocols (e.g., emergency procedures)
        
        Query: {query}
        
        Return as JSON with entity types and values.
        """)
        
        # Graph RAG response generation prompt
        self.response_prompt = ChatPromptTemplate.from_template("""
        You are an aviation customer support assistant. Use the provided context to answer the query accurately and professionally.
        
        Query: {query}
        
        Graph Context: {graph_context}
        Vector Context: {vector_context}
        
        Guidelines:
        - Be precise and accurate with aviation terminology
        - Include relevant safety information when applicable
        - Provide actionable information
        - Cite sources when possible
        - Maintain professional tone
        
        Answer:
        """)
    
    async def process_query(self, query: str, user_context: Dict[str, Any] = None) -> GraphRAGResponse:
        """Main query processing pipeline"""
        
        logger.info("Processing query", query=query)
        
        # Step 1: Intent classification
        intent = await self._classify_intent(query)
        
        # Step 2: Entity extraction
        entities = await self._extract_entities(query)
        
        # Step 3: Graph traversal
        graph_context = await self._traverse_graph(query, intent, entities)
        
        # Step 4: Vector search
        vector_context = await self._search_vector(query, intent)
        
        # Step 5: Context fusion
        fused_context = await self._fuse_context(graph_context, vector_context)
        
        # Step 6: Response generation
        response = await self._generate_response(query, fused_context, user_context)
        
        # Step 7: Quality assessment
        confidence = await self._assess_confidence(response, query, fused_context)
        
        return GraphRAGResponse(
            answer=response,
            sources=self._extract_sources(graph_context, vector_context),
            confidence=confidence,
            graph_paths=graph_context.get("paths", []),
            vector_sources=vector_context,
            metadata={
                "intent": intent,
                "entities": entities,
                "processing_time": None  # TODO: Add timing
            }
        )
    
    async def _classify_intent(self, query: str) -> str:
        """Classify query intent"""
        try:
            chain = self.intent_prompt | self.llm | StrOutputParser()
            intent = await chain.ainvoke({"query": query})
            logger.info("Intent classified", intent=intent, query=query)
            return intent.strip().lower()
        except Exception as e:
            logger.error("Intent classification failed", error=str(e))
            return "general"
    
    async def _extract_entities(self, query: str) -> List[Dict[str, Any]]:
        """Extract aviation-specific entities"""
        try:
            chain = self.entity_prompt | self.llm | StrOutputParser()
            entities_json = await chain.ainvoke({"query": query})
            # TODO: Parse JSON response
            entities = []  # Placeholder
            logger.info("Entities extracted", entities=entities, query=query)
            return entities
        except Exception as e:
            logger.error("Entity extraction failed", error=str(e))
            return []
    
    async def _traverse_graph(self, query: str, intent: str, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Traverse Neo4j knowledge graph"""
        try:
            # Build Cypher query based on intent and entities
            cypher_query = self._build_cypher_query(intent, entities)
            
            # Execute graph traversal
            result = await self.graph_service.execute_query(cypher_query)
            
            # Process and structure results
            graph_context = self._process_graph_results(result, intent)
            
            logger.info("Graph traversal completed", 
                       intent=intent, 
                       result_count=len(result))
            
            return graph_context
            
        except Exception as e:
            logger.error("Graph traversal failed", error=str(e))
            return {"nodes": [], "relationships": [], "paths": []}
    
    def _build_cypher_query(self, intent: str, entities: List[Dict[str, Any]]) -> str:
        """Build Cypher query based on intent and entities"""
        
        if intent == "flight_info":
            return """
            MATCH (f:Flight)-[:DEPARTS_FROM]->(dep:Airport)
            MATCH (f)-[:ARRIVES_AT]->(arr:Airport)
            MATCH (f)-[:OPERATED_BY]->(a:Aircraft)
            WHERE f.flight_number CONTAINS $flight_number
            RETURN f, dep, arr, a
            LIMIT 10
            """
        
        elif intent == "safety":
            return """
            MATCH (sp:SafetyProtocol)-[:ENFORCED_BY]->(r:Regulation)
            MATCH (sp)-[:APPLIES_TO]->(e:Equipment)
            WHERE sp.name CONTAINS $protocol_name
            RETURN sp, r, e
            LIMIT 10
            """
        
        elif intent == "maintenance":
            return """
            MATCH (m:Maintenance)-[:PERFORMED_ON]->(e:Equipment)
            MATCH (m)-[:FOLLOWS]->(p:Procedure)
            WHERE e.equipment_id = $equipment_id
            RETURN m, e, p
            LIMIT 10
            """
        
        else:
            return """
            MATCH (n)
            WHERE n.name CONTAINS $search_term
            RETURN n
            LIMIT 5
            """
    
    def _process_graph_results(self, results: List[Dict], intent: str) -> Dict[str, Any]:
        """Process and structure graph query results"""
        nodes = []
        relationships = []
        paths = []
        
        for result in results:
            # Extract nodes and relationships
            for key, value in result.items():
                if hasattr(value, 'labels'):  # Node
                    nodes.append({
                        'id': value.identity,
                        'labels': list(value.labels),
                        'properties': dict(value)
                    })
                elif hasattr(value, 'type'):  # Relationship
                    relationships.append({
                        'id': value.identity,
                        'type': value.type,
                        'properties': dict(value)
                    })
        
        return {
            'nodes': nodes,
            'relationships': relationships,
            'paths': paths,
            'intent': intent
        }
    
    async def _search_vector(self, query: str, intent: str) -> List[Document]:
        """Search vector database for relevant documents"""
        try:
            # Get embeddings for query
            query_embedding = await self.embeddings.aembed_query(query)
            
            # Search vector database
            results = await self.vector_service.search(
                query_embedding,
                k=5,
                filter={"intent": intent}
            )
            
            logger.info("Vector search completed", 
                       results_count=len(results),
                       intent=intent)
            
            return results
            
        except Exception as e:
            logger.error("Vector search failed", error=str(e))
            return []
    
    async def _fuse_context(self, graph_context: Dict[str, Any], 
                           vector_context: List[Document]) -> Dict[str, Any]:
        """Fuse graph and vector context"""
        
        # Combine graph and vector information
        fused_context = {
            'graph_nodes': graph_context.get('nodes', []),
            'graph_relationships': graph_context.get('relationships', []),
            'vector_documents': [doc.page_content for doc in vector_context],
            'combined_context': self._combine_contexts(graph_context, vector_context)
        }
        
        return fused_context
    
    def _combine_contexts(self, graph_context: Dict[str, Any], 
                         vector_context: List[Document]) -> str:
        """Combine graph and vector context into text"""
        
        context_parts = []
        
        # Add graph context
        if graph_context.get('nodes'):
            context_parts.append("Graph Information:")
            for node in graph_context['nodes']:
                context_parts.append(f"- {node['labels'][0]}: {node['properties'].get('name', 'N/A')}")
        
        # Add vector context
        if vector_context:
            context_parts.append("\nRelated Documents:")
            for doc in vector_context:
                context_parts.append(f"- {doc.page_content[:200]}...")
        
        return "\n".join(context_parts)
    
    async def _generate_response(self, query: str, fused_context: Dict[str, Any], 
                                user_context: Dict[str, Any] = None) -> str:
        """Generate final response using LLM"""
        
        try:
            chain = self.response_prompt | self.llm | StrOutputParser()
            
            response = await chain.ainvoke({
                "query": query,
                "graph_context": fused_context.get('combined_context', ''),
                "vector_context": fused_context.get('vector_documents', []),
                "user_context": user_context or {}
            })
            
            logger.info("Response generated", query=query)
            return response
            
        except Exception as e:
            logger.error("Response generation failed", error=str(e))
            return "I apologize, but I'm unable to process your request at the moment. Please try again later."
    
    async def _assess_confidence(self, response: str, query: str, 
                                context: Dict[str, Any]) -> float:
        """Assess confidence in the generated response"""
        
        # Simple confidence assessment based on context availability
        graph_nodes = len(context.get('graph_nodes', []))
        vector_docs = len(context.get('vector_documents', []))
        
        # Base confidence on available context
        confidence = min(0.9, (graph_nodes + vector_docs) / 10.0)
        
        return max(0.1, confidence)  # Minimum 10% confidence
    
    def _extract_sources(self, graph_context: Dict[str, Any], 
                        vector_context: List[Document]) -> List[Dict[str, Any]]:
        """Extract source information for response"""
        
        sources = []
        
        # Add graph sources
        for node in graph_context.get('nodes', []):
            sources.append({
                'type': 'graph',
                'id': node['id'],
                'labels': node['labels'],
                'properties': node['properties']
            })
        
        # Add vector sources
        for i, doc in enumerate(vector_context):
            sources.append({
                'type': 'vector',
                'id': f'vector_{i}',
                'content': doc.page_content[:200],
                'metadata': doc.metadata
            })
        
        return sources

# Global instance
graph_rag_pipeline = GraphRAGPipeline() 