package com.aviation.rag.core.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Represents an entity extracted from a query.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Entity {
    private EntityType type;
    private String value;
    private double confidence;
} 