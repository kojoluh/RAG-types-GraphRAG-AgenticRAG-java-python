package com.onboarding.rag;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Main Spring Boot application for Agentic RAG system.
 * 
 * This application provides a production-ready Agentic RAG system for enterprise
 * employee onboarding, featuring multi-agent orchestration and personalized
 * learning experiences.
 */
@SpringBootApplication
@EnableJpaRepositories
@EnableCaching
@EnableAsync
@EnableScheduling
public class OnboardingAgenticRagApplication {

    public static void main(String[] args) {
        SpringApplication.run(OnboardingAgenticRagApplication.class, args);
    }
} 