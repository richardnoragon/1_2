#!/usr/bin/env python3
"""
Enterprise Project Reorganization Executor
Richard's File Utilities - Zero-Tolerance Reorganization

This script executes the comprehensive reorganization plan to achieve
enterprise beta-release standards.
"""

import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.temp_reorganization_plan/reorganization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnterpriseReorganizer:
    """Enterprise-grade project reorganization executor."""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.backup_dir = self.root_dir / ".reorganization_backup"
        self.moved_files = []
        
    def create_enterprise_directories(self):
        """Create the enterprise-standard directory structure."""
        logger.info("Creating enterprise directory structure...")
        
        directories = [
            # Documentation structure
            "docs/api",
            "docs/architecture", 
            "docs/deployment",
            "docs/development",
            "docs/reports/completion",
            "docs/reports/security", 
            "docs/reports/performance",
            "docs/security",
            "docs/user-guides",
            
            # Scripts structure
            "scripts/build",
            "scripts/deployment",
            "scripts/development/demos",
            "scripts/development/testing",
            "scripts/development/tools",
            "scripts/maintenance",
            
            # Assets structure
            "assets/images/screenshots",
            "assets/images/icons",
            "assets/ui",
            
            # Configuration structure
            "config/application",
            "config/development",
            "config/production",
            "config/testing",
            
            # Build and distribution
            "build/dist",
            "build/temp",
            
            # Test structure reorganization
            "tests/fixtures",
            "tests/integration",
            "tests/unit/rfu/core",
            "tests/unit/rfu/gui",
            "tests/unit/rfu/database",
            "tests/unit/tools/analysis",
            "tests/unit/tools/file-management",
            "tests/unit/tools/file_operations",
            "tests/unit/tools/metadata",
            "tests/unit/tools/network",
            "tests/unit/tools/privacy",
            "tests/unit/tools/security",
            "tests/unit/tools/system",
            "tests/e2e"
        ]
        
        for directory in directories:
            dir_path = self.root_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def reorganize_documentation(self):
        """Reorganize documentation files according to enterprise standards."""
        logger.info("Reorganizing documentation files...")
        
        # Documentation file mappings
        doc_mappings = {
            # Completion reports
            "*COMPLETION*.md": "docs/reports/completion/",
            "*SUMMARY*.md": "docs/reports/completion/", 
            "*REPORT*.md": "docs/reports/completion/",
            
            # Architecture documentation
            "*ARCHITECTURE*.md": "docs/architecture/",
            "*Architecture*.md": "docs/architecture/",
            "RFU_*.md": "docs/architecture/",
            
            # Security documentation
            "*SECURITY*.md": "docs/security/",
            "*Security*.md": "docs/security/",
            
            # Development documentation
            "*IMPLEMENTATION*.md": "docs/development/",
            "*INTEGRATION*.md": "docs/development/",
            "*MENU*.md": "docs/development/",
            
            # Deployment documentation
            "*DEPLOYMENT*.md": "docs/deployment/",
            "*MIGRATION*.md": "docs/deployment/",
            
            # User guides
            "README*.md": "docs/user-guides/",
        }
        
        # Move documentation files
        for pattern, target_dir in doc_mappings.items():
            self._move_files_by_pattern(pattern, target_dir)
    
    def reorganize_scripts(self):
        """Reorganize scripts according to enterprise standards."""
        logger.info("Reorganizing scripts...")
        
        script_mappings = {
            # Demo scripts
            "*demo*.py": "scripts/development/demos/",
            "enhanced_*.py": "scripts/development/demos/",
            "organized_*.py": "scripts/development/demos/",
            
            # Test scripts
            "test_*.py": "scripts/development/testing/",
            "*test*.py": "scripts/development/testing/",
            "comprehensive_*.py": "scripts/development/testing/",
            
            # Maintenance scripts
            "*validation*.py": "scripts/maintenance/",
            "*corrector*.py": "scripts/maintenance/",
            "fix_*.py": "scripts/maintenance/",
            
            # Development tools
            "open_*.py": "scripts/development/tools/",
            "*integration*.py": "scripts/development/tools/",
        }
        
        for pattern, target_dir in script_mappings.items():
            self._move_files_by_pattern(pattern, target_dir)
    
    def reorganize_assets(self):
        """Reorganize asset files."""
        logger.info("Reorganizing assets...")
        
        # Move screenshots
        if (self.root_dir / "assets/images/screenshots").exists():
            for img_file in self.root_dir.glob("*.png"):
                if "screenshot" in img_file.name.lower():
                    self._move_file(img_file, "assets/images/screenshots/")
        
        # Move existing assets
        if (self.root_dir / "assets").exists():
            # Assets are already in a good structure, just ensure proper organization
            logger.info("Assets directory already properly structured")
    
    def reorganize_configuration(self):
        """Reorganize configuration files."""
        logger.info("Reorganizing configuration files...")
        
        config_mappings = {
            "*.json": "config/application/",
            "*.yaml": "config/application/",
            "*.yml": "config/application/",
            "*.ini": "config/application/",
            "config*.py": "config/application/",
        }
        
        # Move standalone configuration files in root
        for pattern, target_dir in config_mappings.items():
            for config_file in self.root_dir.glob(pattern):
                if config_file.is_file() and config_file.parent == self.root_dir:
                    self._move_file(config_file, target_dir)
    
    def clean_root_directory(self):
        """Clean root directory to enterprise standards (≤10 files)."""
        logger.info("Cleaning root directory to enterprise standards...")
        
        # Files that MUST stay in root
        keep_in_root = {
            'main.py',
            'README.md', 
            'LICENSE',
            'requirements.txt',
            'pytest.ini',
            '.gitignore',
            'pyproject.toml',
            '.pre-commit-config.yaml'
        }
        
        # Check all files in root
        root_files = [f for f in self.root_dir.iterdir() if f.is_file()]
        
        logger.info(f"Found {len(root_files)} files in root directory")
        
        files_to_move = []
        for file_path in root_files:
            if file_path.name not in keep_in_root:
                files_to_move.append(file_path)
        
        logger.info(f"Moving {len(files_to_move)} files from root directory")
        
        # Move files based on type
        for file_path in files_to_move:
            if file_path.suffix == '.md':
                if 'completion' in file_path.name.lower() or 'summary' in file_path.name.lower():
                    self._move_file(file_path, "docs/reports/completion/")
                elif 'security' in file_path.name.lower():
                    self._move_file(file_path, "docs/security/")
                else:
                    self._move_file(file_path, "docs/development/")
            elif file_path.suffix == '.py':
                if 'test' in file_path.name:
                    self._move_file(file_path, "scripts/development/testing/")
                elif 'demo' in file_path.name:
                    self._move_file(file_path, "scripts/development/demos/")
                else:
                    self._move_file(file_path, "scripts/maintenance/")
            elif file_path.suffix in ['.json', '.yaml', '.yml']:
                self._move_file(file_path, "config/application/")
            elif file_path.suffix == '.png':
                self._move_file(file_path, "assets/images/screenshots/")
            else:
                # Move other files to appropriate locations
                self._move_file(file_path, "docs/development/")
    
    def reorganize_source_structure(self):
        """Reorganize source code structure for enterprise standards."""
        logger.info("Reorganizing source code structure...")
        
        src_dir = self.root_dir / "src"
        if not src_dir.exists():
            logger.warning("Source directory not found")
            return
        
        # Create new source structure
        new_structure = [
            "src/rfu/core",
            "src/rfu/gui/common",
            "src/rfu/gui/dialogs",
            "src/rfu/gui/widgets",
            "src/rfu/gui/windows",
            "src/rfu/database/models",
            "src/rfu/database/migrations",
            "src/rfu/utils",
            "src/tools/analysis",
            "src/tools/file-management",
            "src/tools/file_operations",
            "src/tools/metadata",
            "src/tools/network",
            "src/tools/privacy",
            "src/tools/security",
            "src/tools/system"
        ]
        
        for directory in new_structure:
            (self.root_dir / directory).mkdir(parents=True, exist_ok=True)
        
        # Move utilities to tools structure
        utilities_dir = src_dir / "utilities"
        if utilities_dir.exists():
            tools_dir = src_dir / "tools"
            
            # Map utilities categories to tools
            category_mappings = {
                "analysis": "analysis",
                "file_management": "file-management", 
                "file_operations": "file_operations",
                "metadata": "metadata",
                "network": "network",
                "privacy": "privacy",
                "security": "security",
                "system": "system"
            }
            
            for old_category, new_category in category_mappings.items():
                old_path = utilities_dir / old_category
                new_path = tools_dir / new_category
                
                if old_path.exists():
                    if new_path.exists():
                        # Merge directories
                        self._merge_directories(old_path, new_path)
                    else:
                        # Move entire directory
                        shutil.move(str(old_path), str(new_path))
                        logger.info(f"Moved {old_path} to {new_path}")
    
    def _move_files_by_pattern(self, pattern: str, target_dir: str):
        """Move files matching pattern to target directory."""
        target_path = self.root_dir / target_dir
        target_path.mkdir(parents=True, exist_ok=True)
        
        for file_path in self.root_dir.glob(pattern):
            if file_path.is_file() and file_path.parent == self.root_dir:
                self._move_file(file_path, target_dir)
    
    def _move_file(self, source_path: Path, target_dir: str):
        """Move a single file to target directory."""
        target_path = self.root_dir / target_dir
        target_path.mkdir(parents=True, exist_ok=True)
        
        destination = target_path / source_path.name
        
        try:
            shutil.move(str(source_path), str(destination))
            self.moved_files.append({
                'source': str(source_path),
                'destination': str(destination),
                'timestamp': datetime.now().isoformat()
            })
            logger.info(f"Moved {source_path.name} to {target_dir}")
        except Exception as e:
            logger.error(f"Failed to move {source_path}: {e}")
    
    def _merge_directories(self, source_dir: Path, target_dir: Path):
        """Merge source directory into target directory."""
        for item in source_dir.iterdir():
            if item.is_file():
                destination = target_dir / item.name
                if destination.exists():
                    # Handle conflicts by adding timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    stem = destination.stem
                    suffix = destination.suffix
                    destination = target_dir / f"{stem}_{timestamp}{suffix}"
                
                shutil.move(str(item), str(destination))
                logger.info(f"Merged file {item.name} to {target_dir}")
            elif item.is_dir():
                target_subdir = target_dir / item.name
                target_subdir.mkdir(exist_ok=True)
                self._merge_directories(item, target_subdir)
        
        # Remove empty source directory
        try:
            source_dir.rmdir()
            logger.info(f"Removed empty directory {source_dir}")
        except OSError:
            logger.warning(f"Could not remove {source_dir} - not empty")
    
    def create_backup(self):
        """Create backup before reorganization."""
        logger.info("Creating backup before reorganization...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        # Backup critical files
        backup_patterns = ['*.py', '*.md', '*.json', '*.yaml', '*.yml']
        
        for pattern in backup_patterns:
            for file_path in self.root_dir.glob(pattern):
                if file_path.is_file() and file_path.parent == self.root_dir:
                    backup_file = self.backup_dir / file_path.name
                    backup_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, backup_file)
        
        logger.info(f"Backup created at {self.backup_dir}")
    
    def generate_report(self):
        """Generate reorganization report."""
        report = {
            'reorganization_timestamp': datetime.now().isoformat(),
            'total_files_moved': len(self.moved_files),
            'moved_files': self.moved_files,
            'enterprise_compliance': {
                'root_directory_files': len([f for f in self.root_dir.iterdir() if f.is_file()]),
                'max_allowed_root_files': 10,
                'compliance_status': 'PASS' if len([f for f in self.root_dir.iterdir() if f.is_file()]) <= 10 else 'FAIL'
            }
        }
        
        report_file = self.root_dir / '.temp_reorganization_plan/reorganization_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Reorganization report saved to {report_file}")
        return report
    
    def execute_full_reorganization(self):
        """Execute the complete enterprise reorganization."""
        logger.info("Starting enterprise project reorganization...")
        
        try:
            # Phase 1: Create backup
            self.create_backup()
            
            # Phase 2: Create directory structure
            self.create_enterprise_directories()
            
            # Phase 3: Reorganize by category
            self.reorganize_documentation()
            self.reorganize_scripts()
            self.reorganize_assets()
            self.reorganize_configuration()
            
            # Phase 4: Clean root directory
            self.clean_root_directory()
            
            # Phase 5: Reorganize source structure
            self.reorganize_source_structure()
            
            # Phase 6: Generate report
            report = self.generate_report()
            
            logger.info("Enterprise reorganization completed successfully!")
            logger.info(f"Files moved: {report['total_files_moved']}")
            logger.info(f"Root directory compliance: {report['enterprise_compliance']['compliance_status']}")
            
            return report
            
        except Exception as e:
            logger.error(f"Reorganization failed: {e}")
            raise

def main():
    """Main execution function."""
    reorganizer = EnterpriseReorganizer()
    report = reorganizer.execute_full_reorganization()
    
    print("\n" + "="*60)
    print("ENTERPRISE REORGANIZATION COMPLETED")
    print("="*60)
    print(f"Total files moved: {report['total_files_moved']}")
    print(f"Root directory compliance: {report['enterprise_compliance']['compliance_status']}")
    print(f"Root directory file count: {report['enterprise_compliance']['root_directory_files']}/10")
    print("\nDetailed report: .temp_reorganization_plan/reorganization_report.json")
    print("Backup location: .reorganization_backup/")
    
if __name__ == "__main__":
    main()