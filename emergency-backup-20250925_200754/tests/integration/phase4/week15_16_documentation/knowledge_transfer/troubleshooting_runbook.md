# Phase 4 Optimization Troubleshooting Runbook

**Version:** 1.0.0  
**Last Updated:** September 4, 2025  
**Maintained By:** RFU Testing Team

## Quick Reference

### Emergency Contacts

- **Technical Lead**: Phase 4 Optimization Expert
- **DevOps Support**: Infrastructure and CI/CD Issues
- **QA Lead**: Test Reliability and Quality Issues

### System Status Check

```bash
# Quick system health check
python tests/integration/phase4/run_phase4_tests.py --categories validation --no-reports

# Expected: All systems operational, < 2 minute execution
```

---

## Common Issues and Solutions

### 1. Parallel Execution Issues

#### Issue: Tests Not Running in Parallel

**Symptoms:**

- Tests executing sequentially despite parallel configuration
- Single worker utilization
- No performance improvement

**Diagnosis:**

```python
from phase4.week13_14_optimization.parallel_execution.test_scheduler import TestScheduler

scheduler = TestScheduler()
system_resources = scheduler._get_system_resources()

print(f"CPU cores available: {system_resources['cpu_count']}")
print(f"Memory available: {system_resources['memory_available_mb']:.0f}MB")

# Check test grouping
test_files = ['test_example.py']
groups = scheduler.create_optimal_test_groups(test_files, max_workers=4)
print(f"Test groups created: {len(groups)}")
```

**Solutions:**

1. **System Resources**: Ensure sufficient CPU cores and memory
2. **Test Dependencies**: Review test dependency configuration
3. **Worker Limits**: Adjust max_workers parameter
4. **Test Grouping**: Verify tests can be grouped for parallel execution

**Prevention:**

- Regular system resource monitoring
- Test dependency documentation
- Parallel execution validation in CI/CD

#### Issue: Worker Processes Hanging

**Symptoms:**

- Workers not completing execution
- Tests timing out
- High memory usage without progress

**Diagnosis:**

```bash
# Check for hanging processes
ps aux | grep pytest
ps aux | grep python | grep test

# Monitor resource usage
top -p $(pgrep -f "pytest")
```

**Solutions:**

1. **Kill Hanging Processes**: `pkill -f "pytest.*test_"`
2. **Increase Timeouts**: Adjust worker timeout settings
3. **Resource Cleanup**: Implement proper test cleanup
4. **Worker Restart**: Restart worker pool

**Emergency Recovery:**

```python
# Emergency worker cleanup
import psutil
import signal

# Find and terminate hanging test processes
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        if 'pytest' in ' '.join(proc.info['cmdline']):
            if proc.create_time() < time.time() - 600:  # Older than 10 minutes
                proc.terminate()
    except:
        pass
```

### 2. Flaky Test Detection Issues

#### Issue: False Positive Flaky Test Detection

**Symptoms:**

- Stable tests marked as flaky
- High false positive rate
- Unnecessary remediation attempts

**Diagnosis:**

```python
from phase4.week13_14_optimization.flaky_test_detection.flaky_detector import FlakyTestDetector

detector = FlakyTestDetector()

# Check detection thresholds
print(f"Flaky threshold: {detector.flaky_threshold}")
print(f"Confidence threshold: {detector.confidence_threshold}")

# Review specific test analysis
test_name = 'problematic_test'
analysis = detector.analyze_failure_patterns(test_name)
print(f"Failure analysis: {analysis}")
```

**Solutions:**

1. **Adjust Thresholds**: Increase flaky_threshold to 0.10 (10%)
2. **Increase Confidence**: Require higher confidence_threshold (0.90)
3. **Extend Analysis Window**: Use longer analysis_window_days (45-60 days)
4. **Manual Review**: Implement manual review for borderline cases

**Configuration Adjustment:**

```python
# Adjust detection sensitivity
detector = FlakyTestDetector()
detector.flaky_threshold = 0.10  # 10% instead of 5%
detector.confidence_threshold = 0.90  # 90% instead of 85%
detector.analysis_window_days = 45  # 45 days instead of 30
```

#### Issue: Flaky Tests Not Being Detected

**Symptoms:**

- Known flaky tests not identified
- Low detection rate
- Continuing test reliability issues

**Diagnosis:**

```python
# Check detection database
detector = FlakyTestDetector()

# Verify test execution history
with sqlite3.connect(detector.db_path) as conn:
    cursor = conn.execute("""
        SELECT test_name, COUNT(*) as runs, 
               SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failures
        FROM test_execution_history 
        GROUP BY test_name
        HAVING runs >= 10
    """)
    
    for test_name, runs, failures in cursor.fetchall():
        failure_rate = failures / runs
        print(f"{test_name}: {failure_rate:.1%} failure rate ({failures}/{runs})")
```

**Solutions:**

1. **Verify Data Collection**: Ensure test executions are being recorded
2. **Lower Thresholds**: Decrease flaky_threshold temporarily
3. **Manual Analysis**: Manually analyze suspected flaky tests
4. **Database Check**: Verify database connectivity and data integrity

### 3. Resource Optimization Issues

#### Issue: High Memory Usage Despite Optimization

**Symptoms:**

- Memory usage not decreasing
- Out of memory errors
- Poor optimization effectiveness

**Diagnosis:**

```python
from phase4.week13_14_optimization.resource_optimization.resource_optimizer import ResourceOptimizer

optimizer = ResourceOptimizer()

# Check current resource usage
stats = optimizer._get_current_resource_stats()
print(f"Current memory: {stats['memory_mb']:.1f}MB")
print(f"Memory percent: {stats['memory_percent']:.1f}%")

# Check resource pools
for pool_name, pool in optimizer.resource_pools.items():
    utilization = len(pool.allocated_resources) / pool.max_size
    print(f"Pool {pool_name}: {utilization:.1%} utilization")
```

**Solutions:**

1. **Force Aggressive Cleanup**: Use 'aggressive' optimization level
2. **Increase Pool Limits**: Adjust resource pool sizes
3. **Memory Leak Detection**: Enable memory leak detection
4. **Garbage Collection**: Force manual garbage collection

**Emergency Memory Recovery:**

```python
# Emergency memory optimization
import gc

# Force aggressive garbage collection
for _ in range(3):
    collected = gc.collect()
    print(f"Collected {collected} objects")

# Clear resource pools
optimizer = ResourceOptimizer()
optimizer.resource_pools.clear()
optimizer._setup_resource_pools()

# Apply aggressive optimization
result = optimizer.optimize_test_environment('aggressive')
print(f"Memory after optimization: {result['resource_stats_after']['memory_mb']:.1f}MB")
```

#### Issue: CPU Usage Not Optimizing

**Symptoms:**

- High CPU usage persisting
- Poor CPU efficiency scores
- System slowdown during tests

**Solutions:**

1. **Reduce Worker Count**: Lower max_workers parameter
2. **CPU Affinity**: Set CPU affinity for test processes
3. **Priority Adjustment**: Lower test process priority
4. **Background Process Check**: Identify competing processes

### 4. Performance Monitoring Issues

#### Issue: Performance Monitor Not Collecting Data

**Symptoms:**

- Empty performance reports
- No monitoring snapshots
- Missing performance metrics

**Diagnosis:**

```python
from phase4.week13_14_optimization.performance_monitoring import PerformanceMonitor

monitor = PerformanceMonitor()

# Test monitoring functionality
monitor.start_monitoring('diagnostic_test')
time.sleep(5)
snapshots = monitor.stop_monitoring()

print(f"Snapshots collected: {len(snapshots)}")
if snapshots:
    print(f"Latest snapshot: {snapshots[-1]}")
```

**Solutions:**

1. **Database Permissions**: Check database file permissions
2. **Monitoring Thread**: Verify monitoring thread is starting
3. **System Permissions**: Ensure psutil has necessary permissions
4. **Storage Space**: Check available disk space

#### Issue: Performance Regression Alerts

**Symptoms:**

- Frequent performance regression alerts
- Declining performance grades
- Increasing execution times

**Investigation Steps:**

```python
# Analyze performance trends
monitor = PerformanceMonitor()
report = monitor.generate_performance_report(time_window_hours=168)  # 7 days

# Check for specific regressions
performance_summary = report.get('performance_summary', {})
print(f"Duration trend: {performance_summary.get('duration', {})}")
print(f"CPU trend: {performance_summary.get('cpu_usage', {})}")
print(f"Memory trend: {performance_summary.get('memory_usage', {})}")

# Review optimization recommendations
for rec in report.get('optimization_recommendations', []):
    print(f"Recommendation: {rec}")
```

**Immediate Actions:**

1. **Baseline Reset**: Recalculate performance baselines
2. **Optimization Level**: Increase optimization level temporarily
3. **Resource Cleanup**: Perform comprehensive resource cleanup
4. **System Analysis**: Check for system-level performance issues

### 5. Selective Execution Issues

#### Issue: Selective Execution Not Reducing Test Count

**Symptoms:**

- All tests being selected despite code changes
- No time savings from selective execution
- Impact analysis not working correctly

**Diagnosis:**

```python
from phase4.week13_14_optimization.selective_execution import SelectiveTestExecutor

executor = SelectiveTestExecutor()

# Check change detection
changes = executor.detect_code_changes('HEAD~3', 'HEAD')
print(f"Changes detected: {len(changes)}")

for change in changes[:5]:  # Show first 5 changes
    print(f"  {change.file_path}: {change.change_type} (impact: {change.impact_score:.2f})")

# Check test impact analysis
impact_analysis = executor.analyze_test_impact(changes)
high_impact = [a for a in impact_analysis if a.priority == 'high']
print(f"High impact tests: {len(high_impact)}")
```

**Solutions:**

1. **Git Repository Check**: Ensure Git repository is accessible
2. **Mapping Update**: Update test-to-code mapping configuration
3. **Impact Thresholds**: Adjust impact scoring thresholds
4. **Dependency Analysis**: Review test dependency mappings

#### Issue: Important Tests Being Skipped

**Symptoms:**

- Critical tests not selected
- Missing coverage for important changes
- Regression issues in production

**Emergency Solution:**

```python
# Force critical test execution
executor = SelectiveTestExecutor()

# Override with force_critical=True
selection_result = executor.select_tests_for_execution(
    base_commit='HEAD~1',
    force_critical=True  # Ensures critical tests always run
)

# Add specific tests to selection
critical_tests = [
    'test_user_journey_complete.py',
    'test_application_lifecycle.py',
    'test_security_validation.py'
]

selected_tests = selection_result['selected_tests']
for critical_test in critical_tests:
    if critical_test not in selected_tests:
        selected_tests.append(critical_test)
```

---

## System Recovery Procedures

### Complete System Reset

```bash
# Stop all optimization processes
pkill -f "phase4.*optimization"

# Clean up databases
rm -f tests/integration/phase4/*.db

# Reset resource pools and caches
python -c "
import gc
gc.collect()
print('System memory cleared')
"

# Restart optimization systems
python tests/integration/phase4/run_phase4_tests.py --optimization-level balanced
```

### Database Recovery

```python
# Recover optimization databases
import sqlite3
import os

databases = [
    'test_performance_history.db',
    'flaky_test_analysis.db', 
    'performance_monitoring.db'
]

for db_file in databases:
    db_path = f'tests/integration/phase4/{db_file}'
    
    if os.path.exists(db_path):
        try:
            # Test database connectivity
            with sqlite3.connect(db_path) as conn:
                conn.execute("SELECT 1")
            print(f"✅ {db_file}: OK")
        except Exception as e:
            print(f"❌ {db_file}: {e}")
            
            # Backup and recreate
            backup_path = f"{db_path}.backup"
            os.rename(db_path, backup_path)
            print(f"🔄 Database backed up and will be recreated")
```

---

## Performance Optimization Checklist

### Daily Checks

- [ ] System resource availability (CPU < 80%, Memory < 85%)
- [ ] Optimization system health scores (> 90%)
- [ ] Recent test execution success rates (> 98%)
- [ ] Flaky test detection alerts
- [ ] Resource pool utilization rates

### Weekly Checks

- [ ] Performance baseline accuracy
- [ ] Optimization effectiveness metrics
- [ ] Test execution time trends
- [ ] Resource optimization ROI analysis
- [ ] Flaky test remediation success rates

### Monthly Checks

- [ ] Comprehensive system health audit
- [ ] Strategic optimization opportunities
- [ ] Training and knowledge transfer needs
- [ ] Infrastructure scaling requirements
- [ ] Optimization strategy evolution

---

## Escalation Procedures

### Level 1: Self-Service (0-2 hours)

**Scope**: Common issues with documented solutions
**Actions**: Follow troubleshooting steps, apply standard fixes
**Resources**: This runbook, documentation, automated tools

### Level 2: Team Support (2-8 hours)

**Scope**: Complex optimization issues, performance problems
**Actions**: Team collaboration, advanced troubleshooting
**Resources**: Team expertise, detailed analysis tools

### Level 3: Expert Consultation (8-24 hours)

**Scope**: System design issues, major performance problems
**Actions**: Expert analysis, potential system modifications
**Resources**: Technical leads, architecture review

### Level 4: Emergency Response (< 1 hour)

**Scope**: Complete system failure, critical production issues
**Actions**: Immediate system recovery, escalation to management
**Resources**: Emergency contacts, rollback procedures

---

## Monitoring and Alerting

### Key Metrics to Monitor

1. **Test Execution Performance**
   - Total execution time trend
   - Parallel execution speedup factor
   - Worker utilization efficiency

2. **System Resource Usage**
   - Memory usage patterns
   - CPU utilization trends
   - I/O operation efficiency

3. **Test Reliability**
   - Flaky test detection rates
   - Test success rate trends
   - Remediation effectiveness

4. **Optimization Effectiveness**
   - Resource optimization ROI
   - Performance improvement trends
   - System stability metrics

### Alert Thresholds

```yaml
Critical Alerts:
  - Test execution time increase > 50%
  - Flaky test rate > 5%
  - System resource usage > 90%
  - Optimization system failure

Warning Alerts:
  - Test execution time increase > 20%
  - Flaky test rate > 2%
  - System resource usage > 80%
  - Performance regression detected

Info Alerts:
  - Weekly performance summary
  - Monthly optimization ROI report
  - Successful remediation notifications
  - System health status updates
```

---

## Knowledge Base

### Frequently Asked Questions

#### Q: How do I know if parallel execution is working?

**A:** Check the test execution logs for multiple worker processes and compare execution time with sequential baseline. Expect 40-60% time reduction with 3-4 workers.

#### Q: What should I do if flaky tests keep appearing?

**A:** Review the failure patterns in the flaky test report, apply recommended remediation strategies, and consider temporary test quarantine for highly unreliable tests.

#### Q: How can I optimize for my specific environment?

**A:** Use the resource optimizer with different optimization levels ('balanced', 'moderate', 'aggressive') and monitor the effectiveness metrics to find the optimal configuration.

#### Q: What do the performance grades mean?

**A:** Performance grades (A+ to D) indicate overall test efficiency based on execution time, resource usage, and efficiency scores. Aim for 80%+ A/B grades.

### Best Practices Summary

1. **Start with 'balanced' optimization** and adjust based on results
2. **Monitor flaky test rates continuously** and remediate promptly
3. **Use selective execution for development** but full suites for production validation
4. **Review performance baselines weekly** to maintain accuracy
5. **Keep optimization systems updated** with latest configurations

### Common Patterns and Solutions

**Pattern**: Gradual performance degradation over time
**Solution**: Regular baseline updates and resource cleanup

**Pattern**: Sudden spike in flaky tests
**Solution**: Check for environment changes, update remediation strategies

**Pattern**: Inconsistent parallel execution performance
**Solution**: Review test dependencies and resource requirements

**Pattern**: Resource optimization not effective
**Solution**: Analyze resource usage patterns and adjust pool sizes

---

This troubleshooting runbook provides immediate solutions for common Phase 4 optimization issues and serves as a comprehensive reference for maintaining optimal system performance.
