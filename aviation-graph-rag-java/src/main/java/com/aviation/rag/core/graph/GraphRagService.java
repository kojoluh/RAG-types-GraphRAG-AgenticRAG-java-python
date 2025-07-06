package com.aviation.rag.core.graph;

import com.aviation.rag.core.model.*;
import com.aviation.rag.core.repository.Neo4jRepository;
import com.aviation.rag.core.vector.VectorService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.ChatClient;
import org.springframework.ai.chat.ChatResponse;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.chat.prompt.PromptTemplate;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;

/**
 * Core Graph RAG service that combines Neo4j knowledge graph traversal
 * with vector search for comprehensive aviation information retrieval.
 */
@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class GraphRagService {

    private final ChatClient chatClient;
    private final VectorStore vectorStore;
    private final Neo4jRepository neo4jRepository;
    private final VectorService vectorService;
    private final QueryIntentClassifier intentClassifier;
    private final EntityExtractor entityExtractor;

    /**
     * Process a query using Graph RAG pipeline.
     */
    public GraphRagResponse processQuery(String query, UserContext userContext) {
        Instant startTime = Instant.now();
        log.info("Processing query: {}", query);

        try {
            // Step 1: Intent classification
            QueryIntent intent = intentClassifier.classifyIntent(query);
            log.debug("Classified intent: {}", intent);

            // Step 2: Entity extraction
            List<Entity> entities = entityExtractor.extractEntities(query);
            log.debug("Extracted entities: {}", entities);

            // Step 3: Graph traversal
            GraphContext graphContext = traverseGraph(query, intent, entities);
            log.debug("Graph context retrieved: {} nodes", graphContext.getNodes().size());

            // Step 4: Vector search
            List<Document> vectorResults = searchVector(query, intent);
            log.debug("Vector search results: {} documents", vectorResults.size());

            // Step 5: Context fusion
            FusedContext fusedContext = fuseContext(graphContext, vectorResults);
            log.debug("Context fusion completed");

            // Step 6: Response generation
            String response = generateResponse(query, fusedContext, userContext);
            log.debug("Response generated");

            // Step 7: Quality assessment
            double confidence = assessConfidence(response, query, fusedContext);

            Duration processingTime = Duration.between(startTime, Instant.now());
            
            return GraphRagResponse.builder()
                    .answer(response)
                    .sources(extractSources(graphContext, vectorResults))
                    .confidence(confidence)
                    .graphPaths(graphContext.getPaths())
                    .vectorSources(vectorResults)
                    .metadata(buildMetadata(intent, entities, processingTime))
                    .processingTime(processingTime.toMillis())
                    .build();

        } catch (Exception e) {
            log.error("Error processing query: {}", query, e);
            return GraphRagResponse.builder()
                    .answer("I apologize, but I encountered an error while processing your request. Please try again.")
                    .confidence(0.0)
                    .processingTime(Duration.between(startTime, Instant.now()).toMillis())
                    .build();
        }
    }

    /**
     * Traverse Neo4j knowledge graph based on intent and entities.
     */
    private GraphContext traverseGraph(String query, QueryIntent intent, List<Entity> entities) {
        try {
            String cypherQuery = buildCypherQuery(intent, entities);
            log.debug("Executing Cypher query: {}", cypherQuery);

            List<Map<String, Object>> results = neo4jRepository.executeQuery(cypherQuery);
            
            return processGraphResults(results, intent);
        } catch (Exception e) {
            log.error("Graph traversal failed", e);
            return new GraphContext();
        }
    }

    /**
     * Build Cypher query based on intent and entities.
     */
    private String buildCypherQuery(QueryIntent intent, List<Entity> entities) {
        switch (intent.getType()) {
            case FLIGHT_INFO:
                return buildFlightInfoQuery(entities);
            case SAFETY:
                return buildSafetyQuery(entities);
            case MAINTENANCE:
                return buildMaintenanceQuery(entities);
            case CUSTOMER_SERVICE:
                return buildCustomerServiceQuery(entities);
            case TECHNICAL:
                return buildTechnicalQuery(entities);
            default:
                return buildGeneralQuery(entities);
        }
    }

    private String buildFlightInfoQuery(List<Entity> entities) {
        String flightNumber = entities.stream()
                .filter(e -> e.getType() == EntityType.FLIGHT_NUMBER)
                .findFirst()
                .map(Entity::getValue)
                .orElse("");

        return """
                MATCH (f:Flight)-[:DEPARTS_FROM]->(dep:Airport)
                MATCH (f)-[:ARRIVES_AT]->(arr:Airport)
                MATCH (f)-[:OPERATED_BY]->(a:Aircraft)
                WHERE f.flight_number CONTAINS $flightNumber
                RETURN f, dep, arr, a
                LIMIT 10
                """.replace("$flightNumber", flightNumber);
    }

    private String buildSafetyQuery(List<Entity> entities) {
        String protocolName = entities.stream()
                .filter(e -> e.getType() == EntityType.SAFETY_PROTOCOL)
                .findFirst()
                .map(Entity::getValue)
                .orElse("");

        return """
                MATCH (sp:SafetyProtocol)-[:ENFORCED_BY]->(r:Regulation)
                MATCH (sp)-[:APPLIES_TO]->(e:Equipment)
                WHERE sp.name CONTAINS $protocolName
                RETURN sp, r, e
                LIMIT 10
                """.replace("$protocolName", protocolName);
    }

    private String buildMaintenanceQuery(List<Entity> entities) {
        String equipmentId = entities.stream()
                .filter(e -> e.getType() == EntityType.EQUIPMENT_ID)
                .findFirst()
                .map(Entity::getValue)
                .orElse("");

        return """
                MATCH (m:Maintenance)-[:PERFORMED_ON]->(e:Equipment)
                MATCH (m)-[:FOLLOWS]->(p:Procedure)
                WHERE e.equipment_id = $equipmentId
                RETURN m, e, p
                LIMIT 10
                """.replace("$equipmentId", equipmentId);
    }

    private String buildCustomerServiceQuery(List<Entity> entities) {
        return """
                MATCH (p:Procedure)-[:APPLIES_TO]->(s:Service)
                WHERE s.category = 'customer_service'
                RETURN p, s
                LIMIT 10
                """;
    }

    private String buildTechnicalQuery(List<Entity> entities) {
        String aircraftType = entities.stream()
                .filter(e -> e.getType() == EntityType.AIRCRAFT_TYPE)
                .findFirst()
                .map(Entity::getValue)
                .orElse("");

        return """
                MATCH (a:Aircraft)-[:HAS_SPECIFICATION]->(s:Specification)
                WHERE a.type CONTAINS $aircraftType
                RETURN a, s
                LIMIT 10
                """.replace("$aircraftType", aircraftType);
    }

    private String buildGeneralQuery(List<Entity> entities) {
        return """
                MATCH (n)
                WHERE n.name CONTAINS $searchTerm
                RETURN n
                LIMIT 5
                """.replace("$searchTerm", entities.stream()
                .map(Entity::getValue)
                .findFirst()
                .orElse(""));
    }

    /**
     * Process and structure graph query results.
     */
    private GraphContext processGraphResults(List<Map<String, Object>> results, QueryIntent intent) {
        List<GraphNode> nodes = new ArrayList<>();
        List<GraphRelationship> relationships = new ArrayList<>();
        List<GraphPath> paths = new ArrayList<>();

        for (Map<String, Object> result : results) {
            for (Map.Entry<String, Object> entry : result.entrySet()) {
                Object value = entry.getValue();
                if (value instanceof org.neo4j.driver.Record) {
                    // Process Neo4j record
                    processNeo4jRecord((org.neo4j.driver.Record) value, nodes, relationships);
                }
            }
        }

        return GraphContext.builder()
                .nodes(nodes)
                .relationships(relationships)
                .paths(paths)
                .intent(intent)
                .build();
    }

    private void processNeo4jRecord(org.neo4j.driver.Record record, 
                                   List<GraphNode> nodes, 
                                   List<GraphRelationship> relationships) {
        // Implementation for processing Neo4j records
        // This would extract nodes and relationships from the record
    }

    /**
     * Search vector database for relevant documents.
     */
    private List<Document> searchVector(String query, QueryIntent intent) {
        try {
            SearchRequest searchRequest = SearchRequest.query(query)
                    .withTopK(5)
                    .withFilterExpression("intent == '" + intent.getType().name() + "'");

            return vectorStore.search(searchRequest)
                    .getResults()
                    .stream()
                    .map(result -> Document.builder()
                            .content(result.getOutput().getContent())
                            .metadata(result.getOutput().getMetadata())
                            .build())
                    .collect(Collectors.toList());
        } catch (Exception e) {
            log.error("Vector search failed", e);
            return new ArrayList<>();
        }
    }

    /**
     * Fuse graph and vector context.
     */
    private FusedContext fuseContext(GraphContext graphContext, List<Document> vectorResults) {
        String combinedContext = combineContexts(graphContext, vectorResults);
        
        return FusedContext.builder()
                .graphNodes(graphContext.getNodes())
                .graphRelationships(graphContext.getRelationships())
                .vectorDocuments(vectorResults.stream()
                        .map(Document::getContent)
                        .collect(Collectors.toList()))
                .combinedContext(combinedContext)
                .build();
    }

    private String combineContexts(GraphContext graphContext, List<Document> vectorResults) {
        StringBuilder context = new StringBuilder();
        
        if (!graphContext.getNodes().isEmpty()) {
            context.append("Graph Information:\n");
            graphContext.getNodes().forEach(node -> 
                context.append("- ").append(node.getLabels().get(0))
                       .append(": ").append(node.getProperties().get("name"))
                       .append("\n"));
        }
        
        if (!vectorResults.isEmpty()) {
            context.append("\nRelated Documents:\n");
            vectorResults.forEach(doc -> 
                context.append("- ").append(doc.getContent().substring(0, 
                    Math.min(200, doc.getContent().length()))).append("...\n"));
        }
        
        return context.toString();
    }

    /**
     * Generate response using Spring AI ChatClient.
     */
    private String generateResponse(String query, FusedContext fusedContext, UserContext userContext) {
        try {
            PromptTemplate template = new PromptTemplate("""
                    You are an aviation customer support assistant. Use the provided context to answer the query accurately and professionally.
                    
                    Query: {query}
                    
                    Graph Context: {graphContext}
                    Vector Context: {vectorContext}
                    
                    Guidelines:
                    - Be precise and accurate with aviation terminology
                    - Include relevant safety information when applicable
                    - Provide actionable information
                    - Cite sources when possible
                    - Maintain professional tone
                    
                    Answer:
                    """);

            Map<String, Object> parameters = Map.of(
                    "query", query,
                    "graphContext", fusedContext.getCombinedContext(),
                    "vectorContext", String.join("\n", fusedContext.getVectorDocuments())
            );

            Prompt prompt = template.create(parameters);
            ChatResponse response = chatClient.call(prompt);
            
            return response.getResult().getOutput().getContent();
        } catch (Exception e) {
            log.error("Response generation failed", e);
            return "I apologize, but I'm unable to process your request at the moment. Please try again later.";
        }
    }

    /**
     * Assess confidence in the generated response.
     */
    private double assessConfidence(String response, String query, FusedContext context) {
        // Simple confidence assessment based on context availability
        int graphNodes = context.getGraphNodes().size();
        int vectorDocs = context.getVectorDocuments().size();
        
        // Base confidence on available context
        double confidence = Math.min(0.9, (graphNodes + vectorDocs) / 10.0);
        
        return Math.max(0.1, confidence); // Minimum 10% confidence
    }

    /**
     * Extract source information for response.
     */
    private List<Source> extractSources(GraphContext graphContext, List<Document> vectorResults) {
        List<Source> sources = new ArrayList<>();
        
        // Add graph sources
        graphContext.getNodes().forEach(node -> 
            sources.add(Source.builder()
                    .type(SourceType.GRAPH)
                    .id(node.getId().toString())
                    .labels(node.getLabels())
                    .properties(node.getProperties())
                    .build()));
        
        // Add vector sources
        for (int i = 0; i < vectorResults.size(); i++) {
            Document doc = vectorResults.get(i);
            sources.add(Source.builder()
                    .type(SourceType.VECTOR)
                    .id("vector_" + i)
                    .content(doc.getContent().substring(0, Math.min(200, doc.getContent().length())))
                    .metadata(doc.getMetadata())
                    .build());
        }
        
        return sources;
    }

    /**
     * Build metadata for the response.
     */
    private Map<String, Object> buildMetadata(QueryIntent intent, List<Entity> entities, Duration processingTime) {
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("intent", intent.getType());
        metadata.put("entities", entities.stream()
                .collect(Collectors.toMap(Entity::getType, Entity::getValue)));
        metadata.put("processing_time_ms", processingTime.toMillis());
        return metadata;
    }
} 