package com.onboarding.rag.core.orchestration;

import com.onboarding.rag.core.agent.*;
import com.onboarding.rag.core.model.*;
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
 * Orchestrates multiple agents for complex query processing in the Agentic RAG system.
 */
@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class AgentOrchestrator {

    private final ChatClient chatClient;
    private final VectorStore vectorStore;
    private final AgentRegistry agentRegistry;
    private final AgentResponseSynthesizer responseSynthesizer;
    private final QualityAssessor qualityAssessor;

    /**
     * Orchestrate multiple agents to process a query.
     */
    public OrchestrationResult orchestrateQuery(String query, AgentContext context) {
        Instant startTime = Instant.now();
        log.info("Starting query orchestration for user: {}", context.getUserId());

        try {
            // Step 1: Route query to appropriate agents
            List<AgentAssignment> agentAssignments = routeToAgents(query, context);
            log.debug("Routed to {} agents", agentAssignments.size());

            // Step 2: Execute agents in parallel
            List<AgentResponse> agentResponses = executeAgents(agentAssignments, context);
            log.debug("Executed {} agents successfully", agentResponses.size());

            // Step 3: Synthesize responses
            String finalResponse = responseSynthesizer.synthesize(query, agentResponses, context);
            log.debug("Response synthesis completed");

            // Step 4: Assess quality
            double confidence = qualityAssessor.assessQuality(query, finalResponse, agentResponses);

            // Step 5: Extract sources
            List<Document> sources = extractSources(agentResponses);

            // Step 6: Generate metadata
            Map<String, Object> metadata = buildMetadata(agentResponses, context);

            Duration processingTime = Duration.between(startTime, Instant.now());
            
            return OrchestrationResult.builder()
                    .finalResponse(finalResponse)
                    .agentResponses(agentResponses)
                    .confidence(confidence)
                    .sources(sources)
                    .metadata(metadata)
                    .processingTime(processingTime.toMillis())
                    .agentSequence(agentResponses.stream()
                            .map(AgentResponse::getAgentRole)
                            .collect(Collectors.toList()))
                    .build();

        } catch (Exception e) {
            log.error("Orchestration failed for query: {}", query, e);
            Duration processingTime = Duration.between(startTime, Instant.now());
            
            return OrchestrationResult.builder()
                    .finalResponse("I encountered an error while processing your request. Please try again.")
                    .agentResponses(new ArrayList<>())
                    .confidence(0.0)
                    .sources(new ArrayList<>())
                    .metadata(Map.of("error", e.getMessage()))
                    .processingTime(processingTime.toMillis())
                    .agentSequence(new ArrayList<>())
                    .build();
        }
    }

    /**
     * Route query to appropriate agents with priorities.
     */
    private List<AgentAssignment> routeToAgents(String query, AgentContext context) {
        List<AgentAssignment> assignments = new ArrayList<>();
        
        for (BaseAgent agent : agentRegistry.getAllAgents()) {
            if (agent.canHandle(query, context)) {
                double priority = agent.getPriority(query, context);
                assignments.add(new AgentAssignment(agent, priority));
            }
        }
        
        // Sort by priority (highest first)
        assignments.sort((a1, a2) -> Double.compare(a2.getPriority(), a1.getPriority()));
        
        log.info("Query routed to {} agents", assignments.size());
        return assignments;
    }

    /**
     * Execute agents in parallel.
     */
    private List<AgentResponse> executeAgents(List<AgentAssignment> assignments, AgentContext context) {
        List<CompletableFuture<AgentResponse>> futures = assignments.stream()
                .map(assignment -> CompletableFuture.supplyAsync(() -> 
                    assignment.getAgent().execute(context)))
                .collect(Collectors.toList());

        // Wait for all agents to complete
        CompletableFuture<Void> allFutures = CompletableFuture.allOf(
                futures.toArray(new CompletableFuture[0]));

        try {
            allFutures.get(); // Wait for completion
            
            return futures.stream()
                    .map(CompletableFuture::join)
                    .filter(response -> response.getConfidence() > 0.0)
                    .sorted((r1, r2) -> Double.compare(r2.getConfidence(), r1.getConfidence()))
                    .collect(Collectors.toList());
                    
        } catch (Exception e) {
            log.error("Agent execution failed", e);
            return new ArrayList<>();
        }
    }

    /**
     * Extract and deduplicate sources from agent responses.
     */
    private List<Document> extractSources(List<AgentResponse> agentResponses) {
        List<Document> allSources = new ArrayList<>();
        Set<String> seenSources = new HashSet<>();

        for (AgentResponse response : agentResponses) {
            for (Document source : response.getSources()) {
                String sourceId = source.getContent().substring(0, Math.min(100, source.getContent().length())) +
                        source.getMetadata().getOrDefault("source", "unknown");
                
                if (!seenSources.contains(sourceId)) {
                    allSources.add(source);
                    seenSources.add(sourceId);
                }
            }
        }

        return allSources;
    }

    /**
     * Build comprehensive metadata for the orchestration result.
     */
    private Map<String, Object> buildMetadata(List<AgentResponse> agentResponses, AgentContext context) {
        Map<String, Object> metadata = new HashMap<>();
        
        metadata.put("user_id", context.getUserId());
        metadata.put("session_id", context.getSessionId());
        metadata.put("agent_count", agentResponses.size());
        metadata.put("agent_roles", agentResponses.stream()
                .map(AgentResponse::getAgentRole)
                .collect(Collectors.toList()));
        
        double totalConfidence = agentResponses.stream()
                .mapToDouble(AgentResponse::getConfidence)
                .sum();
        metadata.put("total_confidence", totalConfidence);
        
        double averageConfidence = agentResponses.isEmpty() ? 0.0 : 
                totalConfidence / agentResponses.size();
        metadata.put("average_confidence", averageConfidence);
        
        long totalProcessingTime = agentResponses.stream()
                .mapToLong(AgentResponse::getProcessingTime)
                .sum();
        metadata.put("total_processing_time", totalProcessingTime);
        
        metadata.put("user_profile_keys", context.getUserProfile().keySet());
        metadata.put("conversation_history_length", context.getConversationHistory().size());
        
        return metadata;
    }

    /**
     * Get orchestrator performance metrics.
     */
    public OrchestratorMetrics getMetrics() {
        return OrchestratorMetrics.builder()
                .totalOrchestrations(0) // TODO: Implement metrics tracking
                .successfulOrchestrations(0)
                .averageProcessingTime(0.0)
                .build();
    }

    /**
     * Get status of all agents.
     */
    public AgentRegistryStatus getAgentStatus() {
        return agentRegistry.getRegistryStatus();
    }

    /**
     * Add an agent to the conversation dynamically.
     */
    public void addAgentToConversation(String agentRole, AgentContext context) {
        log.info("Adding agent to conversation: {}", agentRole);
        // Implementation would depend on specific requirements
    }
} 