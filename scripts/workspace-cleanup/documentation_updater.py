#!/usr/bin/env python3
"""
Documentation Update Tool
Automatically updates project documentation after workspace cleanup
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Set


class DocumentationUpdater:
    """Updates documentation to reflect cleanup changes"""

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.setup_logging()

        # Patterns of obsolete references to remove/update
        self.obsolete_patterns = {
            "migration_files": [
                r"migration_phase\d+\.py",
                r"migration_\w+_executor\.py",
                r"rollback_migration_\w+\.py",
                r"migration_master\.py",
            ],
            "debug_files": [
                r"debug_\w+\.py",
                r"fix_\w+\.py",
                r"diagnostic_\w+\.py",
            ],
            "backup_dirs": [
                r"\.reorganization_backup",
                r"\.temp_reorganization_plan",
                r"migration_backup_\w+",
                r"MIGRATION_BACKUP_\w+",
            ],
            "legacy_files": [
                r"main_dual_interface\.py",
                r"main_corrected_dual_interface\.py",
                r"main_\w+\.py",
            ],
            "preserve_dirs": [
                r"\.roo",
                r"\.kilocode",
            ],
        }

        # Documentation files to update
        self.doc_files = [
            "README.md",
            "README_Migration.md",
            "docs/**/*.md",
            "*.md",
            ".github/**/*.md",
        ]

    def setup_logging(self):
        """Setup logging for documentation updates"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def find_documentation_files(self) -> List[Path]:
        """Find all documentation files in workspace"""
        doc_files = []

        for pattern in self.doc_files:
            matches = list(self.workspace_root.glob(pattern))
            doc_files.extend(matches)

            # Also search recursively
            matches = list(self.workspace_root.rglob(pattern))
            doc_files.extend(matches)

        # Remove duplicates and return sorted
        return sorted(list(set(doc_files)))

    def analyze_document(self, file_path: Path) -> Dict:
        """Analyze a document for obsolete references"""
        analysis = {
            "file": str(file_path.relative_to(self.workspace_root)),
            "obsolete_references": [],
            "update_suggestions": [],
            "needs_update": False,
        }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for obsolete patterns
            for category, patterns in self.obsolete_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        analysis["obsolete_references"].append(
                            {
                                "category": category,
                                "pattern": pattern,
                                "match": match.group(),
                                "line": content[: match.start()].count("\n")
                                + 1,
                                "context": self._get_line_context(
                                    content, match.start()
                                ),
                            }
                        )
                        analysis["needs_update"] = True

            # Generate update suggestions
            if analysis["needs_update"]:
                analysis["update_suggestions"] = self._generate_suggestions(
                    analysis
                )

        except Exception as e:
            self.logger.warning(f"Failed to analyze {file_path}: {e}")
            analysis["error"] = str(e)

        return analysis

    def _get_line_context(
        self, content: str, position: int, context_lines: int = 2
    ) -> str:
        """Get surrounding lines for context"""
        lines = content.split("\n")
        line_num = content[:position].count("\n")

        start = max(0, line_num - context_lines)
        end = min(len(lines), line_num + context_lines + 1)

        context_lines = lines[start:end]
        return "\n".join(
            f"{start + i + 1:3}: {line}"
            for i, line in enumerate(context_lines)
        )

    def _generate_suggestions(self, analysis: Dict) -> List[str]:
        """Generate update suggestions based on analysis"""
        suggestions = []

        # Count references by category
        categories = {}
        for ref in analysis["obsolete_references"]:
            cat = ref["category"]
            categories[cat] = categories.get(cat, 0) + 1

        # Generate category-specific suggestions
        for category, count in categories.items():
            if category == "migration_files":
                suggestions.append(
                    f"Remove {count} references to migration scripts - "
                    "these have been archived after successful completion"
                )
            elif category == "debug_files":
                suggestions.append(
                    f"Remove {count} references to debug scripts - "
                    "these were temporary development tools"
                )
            elif category == "backup_dirs":
                suggestions.append(
                    f"Update {count} references to backup directories - "
                    "these have been consolidated in archive/"
                )
            elif category == "legacy_files":
                suggestions.append(
                    f"Remove {count} references to legacy main files - "
                    "only src/rfu/main.py is now active"
                )

        return suggestions

    def update_document(
        self, file_path: Path, analysis: Dict, dry_run: bool = True
    ) -> Dict:
        """Update a document based on analysis"""
        if not analysis["needs_update"]:
            return {"updated": False, "reason": "No updates needed"}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            updated_content = original_content
            changes_made = []

            # Apply updates based on category
            for ref in analysis["obsolete_references"]:
                category = ref["category"]
                match_text = ref["match"]

                if category == "migration_files":
                    # Remove entire lines mentioning migration files
                    pattern = r"^.*" + re.escape(match_text) + r".*$"
                    replacement = f"<!-- Removed reference to archived migration script: {match_text} -->"
                    updated_content, count = re.subn(
                        pattern,
                        replacement,
                        updated_content,
                        flags=re.MULTILINE,
                    )
                    if count > 0:
                        changes_made.append(
                            f"Removed migration file reference: {match_text}"
                        )

                elif category == "debug_files":
                    # Remove debug file references
                    pattern = r"^.*" + re.escape(match_text) + r".*$"
                    replacement = f"<!-- Removed reference to archived debug script: {match_text} -->"
                    updated_content, count = re.subn(
                        pattern,
                        replacement,
                        updated_content,
                        flags=re.MULTILINE,
                    )
                    if count > 0:
                        changes_made.append(
                            f"Removed debug file reference: {match_text}"
                        )

                elif category == "backup_dirs":
                    # Update backup directory references to point to archive
                    updated_content = updated_content.replace(
                        match_text, "archive/"
                    )
                    changes_made.append(
                        f"Updated backup directory reference: {match_text} -> archive/"
                    )

                elif category == "legacy_files":
                    # Update legacy main file references
                    if "main_" in match_text:
                        updated_content = updated_content.replace(
                            match_text, "src/rfu/main.py"
                        )
                        changes_made.append(
                            f"Updated main file reference: {match_text} -> src/rfu/main.py"
                        )

            # Add update notice if changes were made
            if changes_made:
                update_notice = f"""
<!-- Documentation updated on {self._get_timestamp()} -->
<!-- Changes made during pre-beta workspace cleanup: -->
<!-- {', '.join(changes_made)} -->

"""
                # Insert at beginning of file after any existing front matter
                lines = updated_content.split("\n")
                insert_pos = 0

                # Skip YAML front matter if present
                if lines and lines[0].strip() == "---":
                    for i, line in enumerate(lines[1:], 1):
                        if line.strip() == "---":
                            insert_pos = i + 1
                            break

                lines.insert(insert_pos, update_notice.strip())
                updated_content = "\n".join(lines)

            # Write updated content
            if not dry_run and updated_content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(updated_content)

            return {
                "updated": updated_content != original_content,
                "changes": changes_made,
                "dry_run": dry_run,
            }

        except Exception as e:
            self.logger.error(f"Failed to update {file_path}: {e}")
            return {"updated": False, "error": str(e)}

    def _get_timestamp(self) -> str:
        """Get formatted timestamp"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def create_new_documentation_structure(self, dry_run: bool = True) -> Dict:
        """Create new consolidated documentation structure"""
        structure = {
            "docs/": {
                "architecture/": [
                    "overview.md",
                    "tool-integration.md",
                    "database-schema.md",
                ],
                "development/": [
                    "setup-guide.md",
                    "testing-guide.md",
                    "contribution-guidelines.md",
                ],
                "user-guide/": [
                    "installation.md",
                    "user-manual.md",
                    "troubleshooting.md",
                ],
                "historical/": [
                    "migration-history.md",
                    "architecture-evolution.md",
                    "deprecated-features.md",
                ],
            }
        }

        created_files = []

        if not dry_run:
            for dir_path, subdirs in structure.items():
                base_path = self.workspace_root / dir_path
                base_path.mkdir(parents=True, exist_ok=True)

                if isinstance(subdirs, dict):
                    for subdir, files in subdirs.items():
                        subdir_path = base_path / subdir
                        subdir_path.mkdir(parents=True, exist_ok=True)

                        for file_name in files:
                            file_path = subdir_path / file_name
                            if not file_path.exists():
                                self._create_doc_template(file_path, file_name)
                                created_files.append(
                                    str(
                                        file_path.relative_to(
                                            self.workspace_root
                                        )
                                    )
                                )
                elif isinstance(subdirs, list):
                    for file_name in subdirs:
                        file_path = base_path / file_name
                        if not file_path.exists():
                            self._create_doc_template(file_path, file_name)
                            created_files.append(
                                str(file_path.relative_to(self.workspace_root))
                            )

        return {
            "structure_created": not dry_run,
            "files_created": created_files,
            "dry_run": dry_run,
        }

    def _create_doc_template(self, file_path: Path, file_name: str):
        """Create documentation template based on file name"""
        templates = {
            "overview.md": "# Architecture Overview\n\nTODO: Document system architecture",
            "setup-guide.md": "# Development Setup Guide\n\nTODO: Document setup process",
            "installation.md": "# Installation Guide\n\nTODO: Document installation process",
            "migration-history.md": "# Migration History\n\nThis document tracks the history of workspace migrations and reorganizations.",
        }

        template = templates.get(
            file_name,
            f"# {file_name.replace('-', ' ').replace('.md', '').title()}\n\nTODO: Add content",
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(template)

    def generate_cleanup_summary(
        self, cleanup_report: Dict, dry_run: bool = True
    ) -> Dict:
        """Generate documentation summary of cleanup changes"""
        summary_content = f"""# Pre-Beta Workspace Cleanup Summary

**Date**: {self._get_timestamp()}
**Cleanup Type**: {'Dry Run' if dry_run else 'Live Cleanup'}

## Overview

This document summarizes the workspace cleanup performed during the transition to pre-beta testing phase.

## Files Removed/Archived

### Migration Artifacts
- **Total**: {cleanup_report.get('summary', {}).get('migration_artifacts', 0)} files
- **Location**: Archived to `archive/pre-beta-cleanup-*/migration-artifacts/`
- **Reason**: Migration phases completed successfully

### Debug Scripts  
- **Total**: {cleanup_report.get('summary', {}).get('debug_artifacts', 0)} files
- **Location**: Archived to `archive/pre-beta-cleanup-*/debug-scripts/`
- **Reason**: Temporary development tools no longer needed

### Legacy Backups
- **Total**: {cleanup_report.get('summary', {}).get('legacy_backups', 0)} items
- **Location**: Archived to `archive/pre-beta-cleanup-*/legacy-backups/`
- **Reason**: Consolidated into organized archive structure

## Current Project Structure

```
src/
├── rfu/                    # Main application package  
│   ├── main.py            # Single entry point
│   ├── hub.py             # Main hub interface
│   └── config_manager.py  # Configuration management
├── tools/                 # Tool modules
└── core/                  # Core system components

docs/
├── architecture/          # System architecture docs
├── development/           # Development guides  
├── user-guide/           # User documentation
└── historical/           # Historical information

tests/
├── unit/                 # Unit tests
├── integration/          # Integration tests  
└── system/              # System tests
```

## Recovery Information

If you need to recover archived files:

```bash
# List archived files
python scripts/workspace-cleanup/archive_recovery.py --list

# Search for specific file
python scripts/workspace-cleanup/archive_recovery.py --search "filename"

# Recover specific file
python scripts/workspace-cleanup/archive_recovery.py --recover "path/to/file" --live-run
```

## Validation Results

"""

        # Add validation results
        validation = cleanup_report.get("validation", {})
        if validation:
            summary_content += f"""
- **Critical Files Present**: {'✅ Yes' if validation.get('critical_files_present') else '❌ No'}
- **Application Imports**: {'✅ Working' if validation.get('application_imports') else '❌ Failed'}
- **Configuration Loads**: {'✅ Working' if validation.get('configuration_loads') else '❌ Failed'}
"""

            if validation.get("issues"):
                summary_content += "\n### Issues Found\n"
                for issue in validation["issues"]:
                    summary_content += f"- ⚠️ {issue}\n"

        summary_content += f"""

## Next Steps

1. Run comprehensive test suite: `python -m pytest tests/ -v`
2. Validate application functionality: `python src/rfu/main.py --test-mode`  
3. Update team on workspace changes
4. Monitor for any issues over next 48 hours

## Archive Information

- **Archive Tag**: `{cleanup_report.get('safety_backup_tag', 'N/A')}`
- **Archive Location**: `{cleanup_report.get('archive_location', 'N/A')}`
- **Recovery Tool**: `scripts/workspace-cleanup/archive_recovery.py`

---

*This document was automatically generated by the workspace cleanup process.*
"""

        summary_file = (
            self.workspace_root
            / f"CLEANUP_SUMMARY_{self._get_timestamp().replace(' ', '_').replace(':', '')}.md"
        )

        if not dry_run:
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(summary_content)

        return {
            "summary_created": not dry_run,
            "summary_file": str(summary_file.relative_to(self.workspace_root)),
            "content_length": len(summary_content),
        }

    def run_full_update(
        self, cleanup_report: Dict, dry_run: bool = True
    ) -> Dict:
        """Run complete documentation update process"""
        self.logger.info(
            f"Starting documentation update ({'dry run' if dry_run else 'live update'})..."
        )

        results = {
            "files_analyzed": 0,
            "files_updated": 0,
            "structure_created": False,
            "summary_created": False,
            "errors": [],
        }

        try:
            # 1. Find and analyze all documentation files
            doc_files = self.find_documentation_files()
            results["files_analyzed"] = len(doc_files)

            self.logger.info(f"Found {len(doc_files)} documentation files")

            # 2. Update each file
            for doc_file in doc_files:
                self.logger.info(
                    f"Analyzing: {doc_file.relative_to(self.workspace_root)}"
                )

                analysis = self.analyze_document(doc_file)
                if analysis["needs_update"]:
                    update_result = self.update_document(
                        doc_file, analysis, dry_run
                    )
                    if update_result["updated"]:
                        results["files_updated"] += 1
                        self.logger.info(
                            f"  Updated with {len(update_result['changes'])} changes"
                        )

            # 3. Create new documentation structure
            structure_result = self.create_new_documentation_structure(dry_run)
            results["structure_created"] = structure_result[
                "structure_created"
            ]

            # 4. Generate cleanup summary
            summary_result = self.generate_cleanup_summary(
                cleanup_report, dry_run
            )
            results["summary_created"] = summary_result["summary_created"]

        except Exception as e:
            self.logger.error(f"Documentation update failed: {e}")
            results["errors"].append(str(e))

        self.logger.info("Documentation update completed!")
        self.logger.info(f"  Files analyzed: {results['files_analyzed']}")
        self.logger.info(f"  Files updated: {results['files_updated']}")

        return results


def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Documentation Update Tool")
    parser.add_argument(
        "--workspace", default=".", help="Workspace root directory"
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only analyze, don't update",
    )
    parser.add_argument(
        "--live-run", action="store_true", help="Actually perform updates"
    )
    parser.add_argument(
        "--cleanup-report", help="Path to cleanup report JSON file"
    )

    args = parser.parse_args()

    workspace_root = Path(args.workspace).resolve()
    dry_run = not args.live_run

    updater = DocumentationUpdater(workspace_root)

    # Load cleanup report if provided
    cleanup_report = {}
    if args.cleanup_report:
        try:
            with open(args.cleanup_report, "r") as f:
                cleanup_report = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load cleanup report: {e}")

    if args.analyze_only:
        # Just analyze files
        doc_files = updater.find_documentation_files()
        print(f"Found {len(doc_files)} documentation files:")

        total_refs = 0
        for doc_file in doc_files:
            analysis = updater.analyze_document(doc_file)
            if analysis["needs_update"]:
                print(f"  📄 {analysis['file']}")
                print(
                    f"     {len(analysis['obsolete_references'])} obsolete references"
                )
                total_refs += len(analysis["obsolete_references"])

        print(f"\nTotal obsolete references found: {total_refs}")
    else:
        # Run full update
        results = updater.run_full_update(cleanup_report, dry_run)

        print("📚 Documentation Update Results:")
        print(f"   Files analyzed: {results['files_analyzed']}")
        print(f"   Files updated: {results['files_updated']}")
        print(
            f"   Structure created: {'Yes' if results['structure_created'] else 'No'}"
        )
        print(
            f"   Summary created: {'Yes' if results['summary_created'] else 'No'}"
        )

        if results["errors"]:
            print("   Errors:")
            for error in results["errors"]:
                print(f"     ❌ {error}")


if __name__ == "__main__":
    main()
