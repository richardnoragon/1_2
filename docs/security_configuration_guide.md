# RFU Hub Security Framework - Security Configuration Guide

## Overview

This guide provides comprehensive instructions for configuring the security features of the RFU Hub Security Framework, covering encryption settings, PII detection rules, permission management, audit logging, and operational security best practices.

## Table of Contents

1. [Security Configuration Overview](#security-configuration-overview)
2. [Encryption Configuration](#encryption-configuration)
3. [PII Detection Configuration](#pii-detection-configuration)
4. [Permission Management Configuration](#permission-management-configuration)
5. [Audit Logging Configuration](#audit-logging-configuration)
6. [Security Event Monitoring](#security-event-monitoring)
7. [Performance and Security Balance](#performance-and-security-balance)
8. [Operational Security Best Practices](#operational-security-best-practices)
9. [Configuration Templates](#configuration-templates)
10. [Security Validation and Testing](#security-validation-and-testing)

---

## Security Configuration Overview

The RFU Hub Security Framework provides multiple layers of configurable security:

### Security Layers
- **Encryption Layer:** AES-256-GCM with PBKDF2 key derivation
- **Detection Layer:** Advanced PII detection with configurable rules
- **Access Layer:** Role-based permission management
- **Audit Layer:** Comprehensive logging and monitoring
- **Monitoring Layer:** Real-time security event detection

### Configuration Files
```
config/
├── security_config.yaml          # Main security configuration
├── encryption_config.yaml        # Encryption-specific settings
├── pii_detection_config.yaml     # PII detection rules
├── permissions_config.yaml       # Permission system settings
├── audit_config.yaml            # Audit logging configuration
└── monitoring_config.yaml       # Security monitoring settings
```

---

## Encryption Configuration

### Basic Encryption Configuration

```yaml
# config/encryption_config.yaml
encryption:
  algorithm: "AES-256-GCM"
  key_derivation:
    method: "PBKDF2-HMAC-SHA256"
    iterations: 100000
    salt_size: 32
  nonce_size: 12
  integrity:
    method: "HMAC-SHA256"
    key_size: 32
  
  # Performance tuning
  performance:
    target_latency_ms: 100
    batch_size: 1000
    memory_limit_mb: 512
    
  # Security hardening
  security:
    timing_attack_protection: true
    secure_memory_cleanup: true
    constant_time_comparisons: true
```

### Advanced Encryption Settings

```yaml
# Advanced encryption configuration
encryption_advanced:
  # Key management
  key_management:
    rotation_interval_days: 90
    backup_key_count: 3
    key_strength_validation: true
    
  # User isolation
  user_isolation:
    per_user_salts: true
    cross_user_protection: true
    session_based_keys: false
    
  # Compliance settings
  compliance:
    fips_mode: false
    audit_all_operations: true
    export_restrictions: true
```

### Encryption Performance Tuning

```python
# Python configuration for encryption performance
ENCRYPTION_PERFORMANCE_CONFIG = {
    'batch_processing': {
        'enabled': True,
        'batch_size': 1000,
        'parallel_workers': 4
    },
    'memory_optimization': {
        'streaming_encryption': True,
        'memory_limit': 512 * 1024 * 1024,  # 512MB
        'cleanup_interval': 100
    },
    'caching': {
        'key_cache_size': 1000,
        'key_cache_ttl': 3600,  # 1 hour
        'nonce_cache_size': 10000
    }
}
```

---

## PII Detection Configuration

### PII Detection Rules

```yaml
# config/pii_detection_config.yaml
pii_detection:
  # Global settings
  global:
    enabled: true
    confidence_threshold: 0.7
    enhanced_security_threshold: 0.9
    
  # Detection rules
  rules:
    personal_names:
      enabled: true
      patterns:
        - "first_last_name"
        - "title_name"
        - "full_name_variations"
      confidence_weight: 0.8
      
    ssn_patterns:
      enabled: true
      patterns:
        - "\\d{3}-\\d{2}-\\d{4}"
        - "\\d{9}"
        - "\\d{3}\\s\\d{2}\\s\\d{4}"
      confidence_weight: 0.95
      
    credit_card:
      enabled: true
      validate_luhn: true
      patterns:
        - "visa"
        - "mastercard"
        - "amex"
        - "discover"
      confidence_weight: 0.9
      
    email_addresses:
      enabled: true
      validate_domain: true
      confidence_weight: 0.85
      
    phone_numbers:
      enabled: true
      country_codes: ["US", "CA", "UK"]
      confidence_weight: 0.8
      
    dates_of_birth:
      enabled: true
      date_formats:
        - "MM/DD/YYYY"
        - "DD/MM/YYYY"
        - "YYYY-MM-DD"
      confidence_weight: 0.75
      
    medical_records:
      enabled: true
      keywords:
        - "medical"
        - "health"
        - "patient"
        - "diagnosis"
      confidence_weight: 0.7
      
    financial_info:
      enabled: true
      keywords:
        - "bank"
        - "account"
        - "financial"
        - "tax"
      confidence_weight: 0.75
```

### Custom PII Rules

```yaml
# Custom PII detection rules
custom_pii_rules:
  # Organization-specific patterns
  employee_id:
    pattern: "EMP\\d{6}"
    confidence: 0.9
    category: "internal_identifier"
    
  project_codes:
    pattern: "PROJ-[A-Z]{3}-\\d{4}"
    confidence: 0.8
    category: "business_sensitive"
    
  # Industry-specific patterns
  healthcare:
    patterns:
      - "patient_id: \\d{8}"
      - "mrn: \\d{10}"
    confidence: 0.95
    category: "healthcare_pii"
    
  financial:
    patterns:
      - "account: \\d{10,12}"
      - "routing: \\d{9}"
    confidence: 0.9
    category: "financial_pii"
```

### PII Detection Performance

```yaml
# PII detection performance settings
pii_performance:
  # Processing optimization
  processing:
    parallel_detection: true
    worker_count: 4
    batch_size: 500
    timeout_seconds: 30
    
  # Memory management
  memory:
    max_memory_mb: 1024
    cleanup_interval: 100
    cache_results: true
    cache_size: 10000
    
  # False positive reduction
  accuracy:
    context_analysis: true
    machine_learning: false
    whitelist_enabled: true
    blacklist_enabled: true
```

---

## Permission Management Configuration

### Role-Based Access Control

```yaml
# config/permissions_config.yaml
permissions:
  # Default permission settings
  defaults:
    new_user_permissions:
      read: true
      write: true
      execute: true
      share: false
      delete: false
      admin: false
      
    pii_directory_permissions:
      read: true
      write: false
      execute: false
      share: false
      delete: false
      admin: false
      
  # Role definitions
  roles:
    standard_user:
      permissions: ["read", "write", "execute"]
      restrictions:
        - "no_pii_access"
        - "limited_sharing"
        
    power_user:
      permissions: ["read", "write", "execute", "share"]
      restrictions:
        - "audit_logged"
        
    administrator:
      permissions: ["read", "write", "execute", "share", "delete", "admin"]
      restrictions: []
      
    security_officer:
      permissions: ["read", "admin"]
      special_access:
        - "pii_directories"
        - "audit_logs"
        - "security_events"
        
  # Permission inheritance
  inheritance:
    enabled: true
    parent_child_relationships: true
    group_permissions: true
    
  # Permission expiration
  expiration:
    enabled: true
    default_ttl_days: 90
    max_ttl_days: 365
    warning_days: 7
```

### Advanced Permission Features

```yaml
# Advanced permission configuration
advanced_permissions:
  # Conditional permissions
  conditional:
    time_based:
      enabled: true
      business_hours_only: false
      timezone: "UTC"
      
    location_based:
      enabled: false
      allowed_networks: []
      geo_restrictions: []
      
    context_based:
      enabled: true
      device_restrictions: false
      application_restrictions: true
      
  # Dynamic permissions
  dynamic:
    risk_based_adjustment: true
    behavior_analysis: false
    machine_learning: false
    
  # Audit requirements
  audit:
    log_all_checks: true
    log_failures_only: false
    retention_days: 365
```

---

## Audit Logging Configuration

### Comprehensive Audit Settings

```yaml
# config/audit_config.yaml
audit_logging:
  # Global audit settings
  global:
    enabled: true
    log_level: "INFO"
    retention_days: 365
    compression_enabled: true
    
  # Event categories
  events:
    directory_operations:
      enabled: true
      log_level: "INFO"
      include_metadata: true
      events:
        - "create"
        - "read"
        - "update"
        - "delete"
        
    security_events:
      enabled: true
      log_level: "WARN"
      immediate_alert: true
      events:
        - "permission_violation"
        - "encryption_failure"
        - "suspicious_activity"
        - "pii_exposure"
        
    authentication_events:
      enabled: true
      log_level: "INFO"
      include_failed_attempts: true
      
    performance_events:
      enabled: false
      log_level: "DEBUG"
      threshold_ms: 1000
      
  # Log destinations
  destinations:
    database:
      enabled: true
      table: "audit_logs"
      batch_size: 100
      
    file:
      enabled: true
      path: "/var/log/rfu/audit.log"
      rotation: "daily"
      max_size_mb: 100
      
    syslog:
      enabled: false
      facility: "local0"
      severity: "info"
      
    external:
      enabled: false
      endpoint: "https://log-collector.example.com"
      authentication: "api_key"
      
  # Performance settings
  performance:
    async_logging: true
    buffer_size: 1000
    flush_interval_seconds: 30
    memory_limit_mb: 128
```

### Audit Log Format Configuration

```yaml
# Audit log formatting
audit_format:
  # Standard format
  standard:
    timestamp_format: "ISO8601"
    timezone: "UTC"
    include_microseconds: true
    
  # Field inclusion
  fields:
    required:
      - "timestamp"
      - "user_id"
      - "operation_type"
      - "resource_id"
      - "result"
      
    optional:
      - "ip_address"
      - "user_agent"
      - "session_id"
      - "request_metadata"
      - "response_metadata"
      - "duration_ms"
      
    sensitive:
      - "encrypted_data"
      - "keys"
      - "passwords"
      
  # Privacy protection
  privacy:
    anonymize_pii: true
    hash_user_ids: false
    redact_sensitive_data: true
```

---

## Security Event Monitoring

### Real-time Security Monitoring

```yaml
# config/monitoring_config.yaml
security_monitoring:
  # Real-time detection
  real_time:
    enabled: true
    check_interval_seconds: 10
    batch_processing: true
    
  # Alert thresholds
  thresholds:
    failed_operations:
      warning: 5
      critical: 10
      time_window_minutes: 15
      
    suspicious_activity:
      warning: 3
      critical: 5
      time_window_minutes: 60
      
    encryption_failures:
      warning: 1
      critical: 3
      time_window_minutes: 5
      
    permission_violations:
      warning: 5
      critical: 10
      time_window_minutes: 30
      
  # Response actions
  responses:
    warning_level:
      - "log_event"
      - "send_notification"
      
    critical_level:
      - "log_event"
      - "send_alert"
      - "notify_security_team"
      - "temporary_lockout"
      
  # Notification settings
  notifications:
    email:
      enabled: true
      recipients: ["security@company.com"]
      template: "security_alert"
      
    sms:
      enabled: false
      recipients: ["+1234567890"]
      
    slack:
      enabled: true
      webhook: "https://hooks.slack.com/services/..."
      channel: "#security-alerts"
      
    webhook:
      enabled: false
      url: "https://monitoring.example.com/alerts"
```

### Advanced Monitoring Features

```yaml
# Advanced monitoring configuration
advanced_monitoring:
  # Anomaly detection
  anomaly_detection:
    enabled: false
    baseline_period_days: 30
    sensitivity: "medium"
    
  # Pattern recognition
  pattern_recognition:
    enabled: true
    attack_patterns:
      - "brute_force"
      - "privilege_escalation"
      - "data_exfiltration"
      
  # Correlation rules
  correlation:
    enabled: true
    rules:
      - name: "multiple_failed_access"
        conditions:
          - "failed_operations > 5"
          - "time_window < 300"
        severity: "high"
        
      - name: "pii_access_after_hours"
        conditions:
          - "pii_access = true"
          - "time_of_day outside business_hours"
        severity: "medium"
```

---

## Performance and Security Balance

### Performance Optimization

```yaml
# Performance vs Security balance
performance_security:
  # Encryption performance
  encryption:
    key_caching: true
    batch_operations: true
    parallel_processing: true
    memory_optimization: true
    
  # PII detection performance
  pii_detection:
    fast_mode: false
    parallel_workers: 4
    cache_results: true
    skip_large_files: false
    
  # Audit logging performance
  audit_logging:
    async_mode: true
    buffer_size: 1000
    batch_writes: true
    compression: true
    
  # Database performance
  database:
    connection_pooling: true
    query_optimization: true
    index_optimization: true
    maintenance_scheduling: true
```

### Security vs Usability

```yaml
# Security vs Usability settings
security_usability:
  # User experience
  user_experience:
    transparent_encryption: true
    minimal_prompts: true
    background_processing: true
    
  # Security enforcement
  security_enforcement:
    strict_mode: false
    progressive_enforcement: true
    user_education: true
    
  # Compliance balance
  compliance:
    regulatory_requirements: true
    business_requirements: true
    user_productivity: true
```

---

## Operational Security Best Practices

### Security Hardening Checklist

```yaml
# Security hardening configuration
security_hardening:
  # System hardening
  system:
    - secure_file_permissions
    - encrypted_storage
    - regular_updates
    - access_controls
    
  # Application hardening
  application:
    - input_validation
    - output_encoding
    - error_handling
    - session_management
    
  # Database hardening
  database:
    - encrypted_connections
    - strong_authentication
    - least_privilege_access
    - regular_backups
    
  # Network hardening
  network:
    - firewall_rules
    - intrusion_detection
    - secure_protocols
    - network_segmentation
```

### Regular Security Maintenance

```yaml
# Regular maintenance schedule
maintenance_schedule:
  daily:
    - check_security_alerts
    - review_failed_operations
    - verify_backup_integrity
    
  weekly:
    - review_audit_logs
    - update_threat_intelligence
    - performance_monitoring
    
  monthly:
    - security_assessment
    - configuration_review
    - user_access_review
    
  quarterly:
    - penetration_testing
    - security_training
    - disaster_recovery_testing
    
  annually:
    - comprehensive_security_audit
    - policy_review
    - compliance_assessment
```

---

## Configuration Templates

### Production Configuration Template

```yaml
# Production security configuration template
production_config:
  encryption:
    algorithm: "AES-256-GCM"
    key_derivation:
      method: "PBKDF2-HMAC-SHA256"
      iterations: 100000
    security_level: "high"
    
  pii_detection:
    enabled: true
    all_rules_enabled: true
    confidence_threshold: 0.8
    
  permissions:
    strict_mode: true
    default_deny: true
    audit_all_access: true
    
  audit_logging:
    enabled: true
    retention_days: 365
    real_time_monitoring: true
    
  monitoring:
    enabled: true
    alert_on_all_security_events: true
    immediate_response: true
```

### Development Configuration Template

```yaml
# Development security configuration template
development_config:
  encryption:
    algorithm: "AES-256-GCM"
    key_derivation:
      method: "PBKDF2-HMAC-SHA256"
      iterations: 10000  # Reduced for performance
    security_level: "medium"
    
  pii_detection:
    enabled: true
    basic_rules_only: true
    confidence_threshold: 0.7
    
  permissions:
    strict_mode: false
    default_allow: true
    audit_changes_only: true
    
  audit_logging:
    enabled: true
    retention_days: 30
    real_time_monitoring: false
    
  monitoring:
    enabled: true
    alert_on_critical_only: true
    development_mode: true
```

### Testing Configuration Template

```yaml
# Testing security configuration template
testing_config:
  encryption:
    algorithm: "AES-256-GCM"
    key_derivation:
      method: "PBKDF2-HMAC-SHA256"
      iterations: 1000  # Minimal for testing speed
    security_level: "testing"
    
  pii_detection:
    enabled: true
    test_patterns_only: true
    confidence_threshold: 0.5
    
  permissions:
    strict_mode: false
    test_mode: true
    bypass_restrictions: true
    
  audit_logging:
    enabled: true
    retention_days: 1
    memory_only: true
    
  monitoring:
    enabled: false
    test_mode: true
```

---

## Security Validation and Testing

### Configuration Validation

```python
# Configuration validation script
def validate_security_config(config_path):
    """Validate security configuration"""
    
    validation_results = {
        'encryption': validate_encryption_config(),
        'pii_detection': validate_pii_config(),
        'permissions': validate_permissions_config(),
        'audit_logging': validate_audit_config(),
        'monitoring': validate_monitoring_config()
    }
    
    # Check for security weaknesses
    security_issues = []
    
    if config.encryption.iterations < 50000:
        security_issues.append("Low PBKDF2 iteration count")
    
    if not config.pii_detection.enabled:
        security_issues.append("PII detection disabled")
    
    if not config.audit_logging.enabled:
        security_issues.append("Audit logging disabled")
    
    return ValidationResult(
        valid=len(security_issues) == 0,
        issues=security_issues,
        recommendations=generate_recommendations(security_issues)
    )
```

### Security Testing

```bash
# Security configuration testing commands
python -m rfu.security.test_encryption --config encryption_config.yaml
python -m rfu.security.test_pii_detection --config pii_detection_config.yaml
python -m rfu.security.test_permissions --config permissions_config.yaml
python -m rfu.security.test_audit_logging --config audit_config.yaml
python -m rfu.security.test_monitoring --config monitoring_config.yaml

# Comprehensive security test
python -m rfu.security.comprehensive_test --config security_config.yaml
```

---

## Support and Resources

For security configuration questions, please refer to:

- **API Documentation:** `docs/api_documentation.md`
- **Database Schema:** `docs/database_schema_documentation.md`
- **Migration Guide:** `docs/migration_guide.md`
- **Troubleshooting Guide:** `docs/troubleshooting_guide.md`

---

**Last Updated:** 2024  
**Configuration Guide Version:** 1.0.0  
**Framework Version:** Phase 1-3 Complete