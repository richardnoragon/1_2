#!/usr/bin/env python3
"""
Test script for progressive installer functionality.
"""

import sys
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from progressive_installer import ProgressiveInstaller
from venv_manager import VirtualEnvironmentManager
from dependency_resolver import DependencyResolver

def test_progressive_installer():
    """Test the progressive installer functionality."""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('test')
    
    print("🧪 Testing Progressive Installer (Phase 3)")
    print("=" * 50)
    
    try:
        # Initialize components
        project_root = Path('..').resolve()
        venv_manager = VirtualEnvironmentManager(project_root, logger)
        dependency_resolver = DependencyResolver(logger)
        progressive_installer = ProgressiveInstaller(
            venv_manager, dependency_resolver, logger
        )
        
        # Test requirements analysis
        requirements_file = project_root / 'requirements.txt'
        print(f"📋 Testing with requirements file: {requirements_file}")
        
        if not requirements_file.exists():
            print(f"❌ Requirements file not found: {requirements_file}")
            return False
        
        # Test parsing requirements
        print("\n1. Testing requirements parsing...")
        if progressive_installer._parse_requirements(requirements_file):
            package_count = len(progressive_installer.packages)
            print(f"✅ Successfully parsed {package_count} packages")
            
            # Show package types
            print("\n2. Package classification:")
            for pkg_type in ['BUILD_TOOLS', 'PURE_PYTHON', 'COMPILED', 'SYSTEM_DEPENDENT']:
                count = sum(1 for pkg in progressive_installer.packages.values() 
                           if pkg.package_type.name == pkg_type)
                if count > 0:
                    print(f"   {pkg_type}: {count} packages")
            
            # Test build requirements check
            print("\n3. Testing build requirements check...")
            if progressive_installer._check_build_requirements():
                print("✅ Build requirements check completed")
            else:
                print("⚠️  Build requirements check had issues")
            
            # Test installation plan creation
            print("\n4. Testing installation plan creation...")
            if progressive_installer._create_installation_plan():
                batch_count = len(progressive_installer.batches)
                print(f"✅ Created installation plan with {batch_count} batches")
                
                # Show batch information
                for i, batch in enumerate(progressive_installer.batches, 1):
                    pkg_names = [pkg.name for pkg in batch.packages]
                    print(f"   Batch {i} ({batch.batch_type}): {len(pkg_names)} packages")
                    if len(pkg_names) <= 5:
                        print(f"     Packages: {', '.join(pkg_names)}")
                    else:
                        print(f"     Packages: {', '.join(pkg_names[:3])} and {len(pkg_names)-3} more")
            else:
                print("❌ Failed to create installation plan")
                return False
            
            print("\n✅ All progressive installer tests passed!")
            return True
            
        else:
            print("❌ Failed to parse requirements")
            return False
            
    except Exception as e:
        print(f"💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_progressive_installer()
    sys.exit(0 if success else 1)