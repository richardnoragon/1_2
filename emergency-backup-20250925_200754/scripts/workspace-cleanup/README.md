# Workspace Cleanup Tools - README

## Overview

This comprehensive suite of tools provides systematic workspace cleanup and organization for projects transitioning to pre-beta testing. The tools ensure safe removal of obsolete migration artifacts, debug scripts, and legacy backups while preserving critical functionality.

## Quick Start

### Windows

```batch
scripts\workspace-cleanup\quick-start.bat
```

### Linux/Mac

```bash
python scripts/workspace-cleanup/cleanup_orchestrator.py --workspace . --verbose
```

## Tool Suite Components

### 1. Master Orchestrator (`cleanup_orchestrator.py`)

**Purpose**: Coordinates the complete cleanup process with all safety measures.

**Usage**:

```bash
# Dry run (recommended first)
python cleanup_orchestrator.py --workspace . --verbose

# Live execution (makes actual changes)
python cleanup_orchestrator.py --workspace . --live-run --verbose
```

**Features**:

- Complete workflow orchestration
- Multi-phase execution (pre-cleanup, cleanup, post-cleanup)
- Comprehensive safety backups
- Team coordination integration
- Automated validation

### 2. Pre-Beta Cleanup Engine (`pre_beta_cleanup.py`)

**Purpose**: Core cleanup engine that identifies and archives obsolete files.

**Usage**:

```bash
# Analysis only
python pre_beta_cleanup.py --workspace .

# Execute cleanup
python pre_beta_cleanup.py --workspace . --live-run
```

**What it removes**:

- Migration phase executors and reports (40+ files)
- Debug scripts and diagnostic tools (25+ files)
- Legacy backup directories (15+ directories)
- Temporary test files and compatibility scripts

### 3. Archive Recovery Tool (`archive_recovery.py`)

**Purpose**: Quick recovery of archived files with search and restore capabilities.

**Usage**:

```bash
# List all archived files
python archive_recovery.py --workspace . --list

# Search for specific file
python archive_recovery.py --workspace . --search "filename"

# Recover specific file
python archive_recovery.py --workspace . --recover "path/to/file" --live-run

# Emergency restore entire archive
python archive_recovery.py --workspace . --emergency-restore "archive-name" --live-run
```

### 4. Documentation Updater (`documentation_updater.py`)

**Purpose**: Updates documentation to reflect workspace changes and removes obsolete references.

**Usage**:

```bash
# Analyze documentation only
python documentation_updater.py --workspace . --analyze-only

# Update documentation
python documentation_updater.py --workspace . --live-run
```

**Updates**:

- Removes references to archived migration scripts
- Updates backup directory paths
- Creates new documentation structure
- Generates cleanup summary

### 5. Team Coordinator (`team_coordinator.py`)

**Purpose**: Manages team communication and coordination during cleanup.

**Usage**:

```bash
# Generate team checklists
python team_coordinator.py --workspace . --checklists

# Send notifications (requires configuration)
python team_coordinator.py --workspace . --pre-cleanup

# Create status dashboard
python team_coordinator.py --workspace . --dashboard status.json
```

### 6. Workspace Maintenance (`workspace_maintenance.py`)

**Purpose**: Ongoing maintenance to prevent future accumulation of outdated artifacts.

**Usage**:

```bash
# Daily maintenance
python workspace_maintenance.py --workspace . --daily

# Weekly maintenance
python workspace_maintenance.py --workspace . --weekly

# Monthly maintenance
python workspace_maintenance.py --workspace . --monthly

# Show metrics
python workspace_maintenance.py --workspace . --metrics
```

## Safety Features

### Multi-Layer Backup System

1. **Git Tags**: Point-in-time snapshots before cleanup
2. **Archive System**: Organized storage of removed files with metadata
3. **File-Level Backup**: Emergency fallback if git is unavailable
4. **Metadata Tracking**: Complete provenance information for all archived files

### Validation Checks

- Critical file presence verification
- Import path validation
- Configuration loading tests
- Application startup validation

### Recovery Options

- Individual file recovery from archives
- Complete rollback to pre-cleanup state
- Selective restoration by category
- Emergency restore procedures

## Configuration

### Team Coordination Config (`config/team-coordination.json`)

```json
{
  "team_members": [
    {
      "name": "Project Lead",
      "email": "lead@company.com",
      "role": "project_lead",
      "notifications": ["all"]
    }
  ],
  "notification_settings": {
    "pre_cleanup": { "lead_time_hours": 48 }
  }
}
```

### Maintenance Config (`config/maintenance.json`)

```json
{
  "quality_thresholds": {
    "max_root_files": 25,
    "max_directory_depth": 6,
    "min_test_coverage": 80
  },
  "daily_tasks": {
    "temp_file_cleanup": { "enabled": true, "max_age_hours": 24 }
  }
}
```

## Execution Workflow

### Recommended Process

1. **Analysis Phase**

   ```bash
   python cleanup_orchestrator.py --workspace . --verbose
   ```

2. **Team Preparation** (48 hours before)

   - Generate team checklists
   - Send pre-cleanup notifications
   - Ensure all work is committed

3. **Execution Phase**

   ```bash
   python cleanup_orchestrator.py --workspace . --live-run --verbose
   ```

4. **Validation Phase**

   - Run test suites
   - Validate application functionality
   - Check documentation updates

5. **Monitoring Phase**
   - Monitor for 48 hours
   - Address any issues
   - Run maintenance tools

## File Organization Results

### Before Cleanup

```
workspace/
├── migration_phase1_executor.py
├── migration_phase2_executor.py
├── debug_layout_simple.py
├── fix_critical_errors.py
├── .reorganization_backup/
├── migration_backup_20250916/
└── ... (150+ files in root)
```

### After Cleanup

```
workspace/
├── src/                          # Clean source code
├── tests/                        # Organized test suites
├── docs/                         # Consolidated documentation
├── archive/                      # Organized archived materials
│   └── pre-beta-cleanup-YYYYMMDD/
├── scripts/workspace-cleanup/    # Cleanup tools
├── requirements.txt
├── README.md
└── ... (<25 files in root)
```

## Archive Structure

```
archive/pre-beta-cleanup-YYYYMMDD/
├── migration-artifacts/
│   ├── executors/
│   ├── reports/
│   └── backups/
├── debug-scripts/
│   ├── debug-tools/
│   └── fix-scripts/
├── legacy-backups/
│   └── reorganization/
└── documentation/
    └── completion-reports/
```

Each archived file includes metadata:

```json
{
  "original_path": "migration_phase1_executor.py",
  "archived_date": "2025-09-24T10:30:00Z",
  "reason": "Pre-beta cleanup: Migration phase completed",
  "safety_level": "low",
  "md5_hash": "abc123...",
  "file_size": 12345
}
```

## Quality Metrics

### Tracked Metrics

- Root directory file count
- Directory structure depth
- Duplicate file detection
- Test coverage percentage
- Log file sizes

### Quality Thresholds

- Maximum 25 files in root directory
- Maximum 6 levels of directory depth
- Minimum 80% test coverage
- Maximum 100MB total log size

## Troubleshooting

### Common Issues

**"Import Error After Cleanup"**

```bash
# Use recovery tool to restore missing files
python archive_recovery.py --search "missing_file.py" --recover --live-run
```

**"Git Backup Failed"**

```bash
# Manual backup creation
git add -A
git commit -m "Manual pre-cleanup backup"
git tag "manual-backup-$(date +%Y%m%d)"
```

**"Application Won't Start"**

```bash
# Check validation results
python cleanup_orchestrator.py --phase post --verbose

# Recovery specific critical files
python archive_recovery.py --recover "src/rfu/main.py" --live-run
```

### Emergency Procedures

**Complete Rollback**

```bash
# Find backup tag
git tag | grep pre-cleanup-backup

# Rollback to specific backup
git reset --hard pre-cleanup-backup-YYYYMMDD_HHMMSS

# Clean workspace
git clean -fd
```

**Partial Recovery**

```bash
# List available archives
python archive_recovery.py --list

# Restore specific category
python archive_recovery.py --category "migration" --list
python archive_recovery.py --recover "specific/file/path" --live-run
```

## Logging and Reports

### Log Locations

- Orchestrator: `logs/cleanup/cleanup-orchestrator-*.log`
- Components: `logs/workspace-cleanup-*.log`
- Maintenance: `logs/maintenance/maintenance-*.log`

### Report Locations

- Cleanup reports: `reports/cleanup/cleanup-orchestration-*.json`
- Maintenance reports: `reports/maintenance/*_maintenance_*.json`
- Team dashboards: `cleanup-dashboard.html`

## Support and Recovery

### Contact Information

- **Primary**: Technical Lead
- **Secondary**: Project Lead
- **Emergency**: Use recovery tools and documentation

### Support Tools

- Archive recovery system with search capabilities
- Complete rollback procedures
- Individual file restoration
- Automated validation and health checks

---

## Development Notes

This tool suite was designed specifically for the RFU project's transition to pre-beta testing. It addresses the unique challenges of:

- Large number of migration artifacts (40+ files)
- Complex backup directory structure (15+ directories)
- Scattered debug and fix scripts (25+ files)
- Need for safe, recoverable cleanup process
- Team coordination during cleanup
- Ongoing maintenance to prevent re-accumulation

The tools emphasize safety, recoverability, and automation while providing comprehensive logging and reporting for audit purposes.
