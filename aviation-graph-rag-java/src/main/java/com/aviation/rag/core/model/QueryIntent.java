package com.aviation.rag.core.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Represents the intent of a user query.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class QueryIntent {
    private IntentType type;
    private double confidence;
    private String description;
} 