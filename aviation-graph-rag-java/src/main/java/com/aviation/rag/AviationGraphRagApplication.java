package com.aviation.rag;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.data.neo4j.repository.config.EnableNeo4jRepositories;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Main Spring Boot application for Aviation Graph RAG system.
 * 
 * This application provides a production-ready Graph RAG system for aviation
 * customer support, leveraging Neo4j knowledge graphs and Spring AI for
 * intelligent information retrieval.
 */
@SpringBootApplication
@EnableNeo4jRepositories
@EnableCaching
@EnableAsync
@EnableScheduling
public class AviationGraphRagApplication {

    public static void main(String[] args) {
        SpringApplication.run(AviationGraphRagApplication.class, args);
    }
} 