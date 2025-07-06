# CI/CD Pipeline Guide

This guide provides comprehensive documentation for the CI/CD pipelines implemented for the RAG Types project, covering both Python and Java implementations.

## Overview

The CI/CD pipeline consists of multiple workflows that ensure code quality, security, performance, and reliable deployments across different environments.

## Workflow Architecture

### 1. Python CI/CD Pipeline (`python-ci-cd.yml`)

**Purpose**: Comprehensive CI/CD pipeline for Python implementations

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Changes in Python project directories

**Jobs**:

#### Code Quality & Security
- **Black**: Code formatting check
- **isort**: Import sorting validation
- **flake8**: Linting with PEP 8 compliance
- **mypy**: Type checking
- **Bandit**: Security linting
- **Safety**: Dependency vulnerability scanning

#### Testing
- **Unit Tests**: pytest with coverage reporting
- **Integration Tests**: Full integration test suite
- **TestContainers**: Containerized testing with real dependencies

#### Security Analysis
- **SAST**: Static Application Security Testing with Semgrep and CodeQL
- **Container Security**: Trivy vulnerability scanning
- **Dependency Scanning**: OWASP Dependency Check

#### Build & Package
- **Poetry Build**: Package creation
- **Docker Build**: Container image creation
- **Artifact Upload**: Package and image storage

#### Deployment
- **Staging Deployment**: Automatic deployment to staging environment
- **Production Deployment**: Manual deployment to production
- **Health Checks**: Post-deployment validation

#### Performance Testing
- **Load Testing**: Locust-based performance testing
- **Monitoring**: Real-time performance monitoring

### 2. Java CI/CD Pipeline (`java-ci-cd.yml`)

**Purpose**: Comprehensive CI/CD pipeline for Java implementations

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Changes in Java project directories

**Jobs**:

#### Code Quality & Security
- **Checkstyle**: Code style validation
- **SpotBugs**: Bug detection
- **PMD**: Code analysis
- **SonarQube**: Code quality analysis
- **OWASP Dependency Check**: Security scanning

#### Testing
- **Unit Tests**: Maven Surefire with JUnit
- **Integration Tests**: TestContainers integration
- **Coverage**: JaCoCo coverage reporting

#### Security Analysis
- **SAST**: Semgrep and CodeQL analysis
- **Container Security**: Trivy and Snyk scanning
- **Dependency Scanning**: OWASP Dependency Check

#### Build & Package
- **Maven Build**: Application compilation and packaging
- **Docker Build**: Container image creation
- **SBOM Generation**: Software Bill of Materials

#### Deployment
- **Staging Deployment**: Kubernetes deployment to staging
- **Production Deployment**: Kubernetes deployment to production
- **Health Checks**: Spring Boot Actuator health endpoints

### 3. Security Scanning & Compliance (`security-scanning.yml`)

**Purpose**: Dedicated security scanning and compliance workflow

**Triggers**:
- Weekly scheduled scans (Mondays at 2 AM)
- Push to main branches
- Manual trigger

**Jobs**:

#### SAST Analysis
- **Semgrep**: Security rule scanning
- **CodeQL**: GitHub's semantic code analysis
- **Bandit**: Python security linting
- **SpotBugs**: Java security analysis

#### Dependency Scanning
- **Safety**: Python dependency vulnerability check
- **OWASP Dependency Check**: Java dependency analysis

#### Container Security
- **Trivy**: Container vulnerability scanning
- **Snyk**: Container security analysis

#### DAST Scanning
- **OWASP ZAP**: Dynamic application security testing
- **Nuclei**: Template-based vulnerability scanning

#### Secrets Scanning
- **TruffleHog**: Git history secrets scanning
- **GitGuardian**: Real-time secrets detection
- **Gitleaks**: Secrets detection

#### Compliance Scanning
- **OpenSCAP**: Security compliance scanning
- **License Compliance**: Dependency license validation
- **SBOM Generation**: Software Bill of Materials

### 4. Performance Testing & Monitoring (`performance-testing.yml`)

**Purpose**: Comprehensive performance testing and monitoring

**Triggers**:
- Weekly scheduled tests (Tuesdays at 3 AM)
- Push to main branches
- Manual trigger

**Jobs**:

#### Load Testing
- **Locust**: Python-based load testing
- **Artillery**: Node.js-based stress testing

#### JMeter Testing
- **Apache JMeter**: Java-based performance testing
- **Custom Test Plans**: RAG-specific test scenarios

#### Performance Monitoring
- **Real-time Monitoring**: Endpoint performance tracking
- **Resource Monitoring**: CPU and memory usage
- **Response Time Analysis**: Latency measurement

#### Memory Profiling
- **Python Profiling**: Memory usage analysis
- **Java Profiling**: JVM memory analysis

### 5. Deployment Pipeline (`deployment.yml`)

**Purpose**: Production-ready deployment with rollback capabilities

**Triggers**:
- Push to main branches
- Manual deployment trigger

**Jobs**:

#### Pre-deployment Validation
- **Environment Validation**: Infrastructure checks
- **Dependency Validation**: Service availability
- **Configuration Validation**: Environment variables

#### Build and Package
- **Multi-language Build**: Python and Java builds
- **Docker Image Creation**: Container packaging
- **Artifact Management**: Package storage

#### Security Scanning
- **Trivy Scanning**: Container vulnerability check
- **Critical/High Severity**: Security threshold enforcement

#### Deployment
- **Staging Deployment**: Kubernetes deployment to staging
- **Production Deployment**: Kubernetes deployment to production
- **Rollback Capability**: Automatic rollback on failure

#### Post-deployment Validation
- **Health Checks**: Service availability verification
- **Performance Tests**: Basic performance validation
- **Security Tests**: Post-deployment security checks

### 6. Quality Gates (`quality-gates.yml`)

**Purpose**: Enforce quality standards and prevent deployment if thresholds are not met

**Triggers**:
- Push to main branches
- Pull requests
- Manual trigger

**Jobs**:

#### Code Quality Gates
- **Formatting**: Black/isort for Python, Checkstyle for Java
- **Linting**: flake8 for Python, PMD for Java
- **Type Checking**: mypy for Python, compiler for Java

#### Test Coverage Gates
- **Coverage Thresholds**: 80% for Python, 75% for Java
- **Test Execution**: Unit and integration tests
- **Coverage Reporting**: HTML and XML reports

#### Security Quality Gates
- **Vulnerability Scanning**: No critical/high vulnerabilities
- **Secrets Detection**: No hardcoded secrets
- **Configuration Validation**: Security configuration checks

#### Performance Quality Gates
- **Response Time**: < 200ms average
- **Throughput**: > 1000 requests/second
- **Error Rate**: < 1%

#### Documentation Quality Gates
- **Completeness**: All functions/classes documented
- **API Documentation**: OpenAPI/Swagger validation
- **README Files**: Project documentation completeness

#### Dependency Quality Gates
- **Vulnerability Check**: No known vulnerabilities
- **License Compliance**: Valid dependency licenses
- **Update Status**: Outdated dependency detection

## Configuration

### Environment Variables

```bash
# Python Configuration
PYTHON_VERSION=3.11
POETRY_VERSION=1.7.1

# Java Configuration
JAVA_VERSION=21
MAVEN_VERSION=3.9.5

# Security Tokens
SNYK_TOKEN=your_snyk_token
SONAR_TOKEN=your_sonarqube_token
SLACK_WEBHOOK_URL=your_slack_webhook

# Kubernetes Configuration
KUBE_CONFIG=base64_encoded_kubeconfig
KUBE_CONFIG_PROD=base64_encoded_production_kubeconfig

# Container Registry
REGISTRY_URL=your_registry_url
REGISTRY_USERNAME=your_registry_username
REGISTRY_PASSWORD=your_registry_password
```

### Secrets Management

Required GitHub Secrets:

1. **Security Tokens**:
   - `SNYK_TOKEN`: Snyk security scanning
   - `SONAR_TOKEN`: SonarQube analysis
   - `SLACK_WEBHOOK_URL`: Slack notifications

2. **Kubernetes Configuration**:
   - `KUBE_CONFIG`: Staging environment kubeconfig
   - `KUBE_CONFIG_PROD`: Production environment kubeconfig

3. **Container Registry**:
   - `REGISTRY_URL`: Container registry URL
   - `REGISTRY_USERNAME`: Registry username
   - `REGISTRY_PASSWORD`: Registry password

## Usage

### Manual Deployment

```bash
# Deploy to staging
gh workflow run deployment.yml -f environment=staging

# Deploy to production
gh workflow run deployment.yml -f environment=production

# Deploy specific version
gh workflow run deployment.yml -f environment=production -f version=v1.2.3
```

### Quality Gate Checks

```bash
# Run quality gates manually
gh workflow run quality-gates.yml

# Check quality gate status
gh run list --workflow=quality-gates.yml
```

### Security Scanning

```bash
# Run security scan manually
gh workflow run security-scanning.yml

# View security results
gh run list --workflow=security-scanning.yml
```

### Performance Testing

```bash
# Run performance tests manually
gh workflow run performance-testing.yml

# View performance results
gh run list --workflow=performance-testing.yml
```

## Monitoring and Alerts

### Slack Notifications

The pipelines send notifications to Slack channels:
- `#deployments`: Deployment status
- `#security`: Security vulnerabilities
- `#performance`: Performance issues
- `#quality`: Quality gate failures

### Email Notifications

Configure email notifications for critical failures:
- Security vulnerabilities
- Quality gate failures
- Deployment failures

### Metrics and Dashboards

Track key metrics:
- **Deployment Success Rate**: > 95%
- **Test Coverage**: > 80% (Python), > 75% (Java)
- **Security Vulnerabilities**: 0 critical/high
- **Performance**: < 200ms response time

## Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check dependency versions
   - Verify environment setup
   - Review build logs

2. **Test Failures**:
   - Check test data
   - Verify service dependencies
   - Review test configuration

3. **Security Failures**:
   - Update vulnerable dependencies
   - Fix security issues in code
   - Review security configuration

4. **Deployment Failures**:
   - Check Kubernetes configuration
   - Verify service health
   - Review deployment logs

### Debugging

```bash
# View workflow logs
gh run view --log

# Download artifacts
gh run download

# Re-run failed workflow
gh run rerun
```

## Best Practices

### Code Quality
- Write comprehensive tests
- Maintain high test coverage
- Follow coding standards
- Use type hints (Python) and annotations (Java)

### Security
- Regular dependency updates
- Security scanning in CI/CD
- Secrets management
- Container security scanning

### Performance
- Load testing before deployment
- Performance monitoring
- Resource optimization
- Caching strategies

### Deployment
- Blue-green deployments
- Rollback capabilities
- Health checks
- Monitoring and alerting

## Customization

### Adding New Projects

1. Update matrix strategies in workflows
2. Add project-specific configurations
3. Update deployment manifests
4. Configure monitoring

### Modifying Quality Gates

1. Update threshold values
2. Add new quality checks
3. Configure notifications
4. Update documentation

### Extending Security Scanning

1. Add new security tools
2. Configure scanning rules
3. Update vulnerability databases
4. Set up custom alerts

## Support

For issues with the CI/CD pipeline:

1. Check workflow logs
2. Review configuration
3. Verify secrets and permissions
4. Contact the DevOps team

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Security Scanning Tools](https://owasp.org/www-project-security-testing-guide/)
- [Performance Testing Guide](https://locust.io/) 