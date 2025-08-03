#!/usr/bin/env python3
"""
Quick dependency analysis script
"""

from scripts.dependency_resolver import DependencyResolver
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('dependency_analysis')

# Initialize dependency resolver
resolver = DependencyResolver(logger)

# Analyze requirements file
requirements_file = Path('requirements.txt')
print('🔍 Analyzing requirements.txt...')
analysis = resolver.analyze_requirements_file(requirements_file)

print(f'📊 Analysis Results:')
print(f'  Total packages: {analysis.get("total_packages", 0)}')
print(f'  Valid packages: {len(analysis.get("valid_packages", []))}')
print(f'  Invalid packages: {len(analysis.get("invalid_packages", []))}')
print(f'  Conflicts: {len(analysis.get("conflicts", []))}')

if analysis.get('conflicts'):
    print('⚠️  Conflicts detected:')
    for conflict in analysis['conflicts']:
        print(f'    - {conflict.get("package", "unknown")}: {conflict.get("severity", "unknown")}')

if analysis.get('suggestions'):
    print('💡 Suggestions:')
    for suggestion in analysis['suggestions']:
        print(f'    - {suggestion}')

print('\n✅ Analysis complete!')