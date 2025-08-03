#!/usr/bin/env python3
"""
Dependency Resolver
==================

This module provides dependency conflict detection and resolution for Python
packages, helping to identify and resolve version conflicts before
installation.

Features:
- Dependency tree analysis and visualization
- Version conflict detection
- Compatibility checking
- Resolution suggestions
- Package availability validation
- Circular dependency detection
"""

import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Set, Union
import logging
from dataclasses import dataclass, field


@dataclass
class PackageInfo:
    """Information about a package."""
    name: str
    version: str
    requirements: List[str]
    available_versions: List[str]
    is_available: bool = True
    conflicts: List[str] = field(default_factory=list)


@dataclass
class DependencyConflict:
    """Information about a dependency conflict."""
    package: str
    conflicting_requirements: List[str]
    suggested_resolution: Optional[str] = None
    severity: str = "medium"  # low, medium, high, critical


class SimpleRequirement:
    """Simple requirement parser for basic package specifications."""
    
    def __init__(self, requirement_string: str):
        """Parse a requirement string.
        
        Args:
            requirement_string: Package requirement (e.g., "package>=1.0")
        """
        self.original = requirement_string.strip()
        self.name = ""
        self.operator = ""
        self.version = ""
        self._parse()
    
    def _parse(self):
        """Parse the requirement string."""
        # Simple regex-like parsing for basic requirements
        req = self.original
        
        # Handle operators
        operators = ['>=', '<=', '==', '!=', '>', '<', '~=']
        for op in operators:
            if op in req:
                parts = req.split(op, 1)
                if len(parts) == 2:
                    self.name = parts[0].strip()
                    self.operator = op
                    self.version = parts[1].strip()
                    return
        
        # No operator found, just package name
        self.name = req.strip()


class DependencyResolver:
    """Advanced dependency resolution and conflict detection."""
    
    def __init__(self, logger: logging.Logger):
        """Initialize the dependency resolver.
        
        Args:
            logger: Logger instance for output
        """
        self.logger = logger
        self.package_cache: Dict[str, PackageInfo] = {}
        self.pypi_cache: Dict[str, Dict] = {}
        
    def analyze_requirements_file(self, requirements_path: Path
                                  ) -> Dict[str, Union[List, Dict, str]]:
        """Analyze a requirements.txt file for conflicts and issues.
        
        Args:
            requirements_path: Path to requirements.txt file
            
        Returns:
            Dictionary with analysis results
        """
        self.logger.info(f"Analyzing requirements file: {requirements_path}")
        
        if not requirements_path.exists():
            self.logger.error(f"Requirements file not found: "
                              f"{requirements_path}")
            return {
                'error': 'File not found',
                'valid_packages': [],
                'invalid_packages': [],
                'conflicts': [],
                'warnings': [],
                'suggestions': []
            }
        
        try:
            # Parse requirements
            requirements = self._parse_requirements_file(requirements_path)
            
            # Analyze each requirement
            analysis = {
                'total_packages': len(requirements),
                'valid_packages': [],
                'invalid_packages': [],
                'conflicts': [],
                'warnings': [],
                'suggestions': []
            }
            
            # Check each package
            for req_str in requirements:
                try:
                    req = SimpleRequirement(req_str)
                    package_info = self._get_package_info(req.name)
                    
                    if package_info.is_available:
                        analysis['valid_packages'].append({
                            'name': req.name,
                            'requirement': (f"{req.operator}{req.version}"
                                            if req.operator else "any"),
                            'latest_version': (
                                package_info.available_versions[0]
                                if package_info.available_versions
                                else 'Unknown'
                            )
                        })
                    else:
                        analysis['invalid_packages'].append({
                            'name': req.name,
                            'requirement': req_str,
                            'reason': 'Package not found on PyPI'
                        })
                        
                except Exception as e:
                    analysis['invalid_packages'].append({
                        'name': req_str,
                        'requirement': req_str,
                        'reason': f'Invalid requirement format: {e}'
                    })
            
            # Detect conflicts
            conflicts = self._detect_conflicts(requirements)
            analysis['conflicts'] = [
                {
                    'package': conflict.package,
                    'conflicting_requirements': (
                        conflict.conflicting_requirements),
                    'severity': conflict.severity,
                    'suggested_resolution': conflict.suggested_resolution
                }
                for conflict in conflicts
            ]
            
            # Generate suggestions
            analysis['suggestions'] = self._generate_suggestions(
                requirements, conflicts)
            
            valid_count = len(analysis['valid_packages'])
            invalid_count = len(analysis['invalid_packages'])
            conflict_count = len(analysis['conflicts'])
            self.logger.info(f"Analysis complete: {valid_count} valid, "
                             f"{invalid_count} invalid, "
                             f"{conflict_count} conflicts")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze requirements: {e}")
            return {
                'error': str(e),
                'valid_packages': [],
                'invalid_packages': [],
                'conflicts': [],
                'warnings': [],
                'suggestions': []
            }
    
    def _parse_requirements_file(self, requirements_path: Path) -> List[str]:
        """Parse requirements.txt file and extract package specifications.
        
        Args:
            requirements_path: Path to requirements file
            
        Returns:
            List of requirement strings
        """
        requirements = []
        
        with open(requirements_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Handle -r includes (recursive requirements)
                if line.startswith('-r '):
                    include_path = requirements_path.parent / line[3:].strip()
                    if include_path.exists():
                        requirements.extend(
                            self._parse_requirements_file(include_path))
                    else:
                        self.logger.warning(f"Include file not found: "
                                            f"{include_path}")
                    continue
                
                # Handle other pip options
                if line.startswith('-'):
                    self.logger.debug(f"Skipping pip option: {line}")
                    continue
                
                # Clean up the requirement string
                req = line.split('#')[0].strip()  # Remove inline comments
                if req:
                    requirements.append(req)
        
        return requirements
    
    def _get_package_info(self, package_name: str) -> PackageInfo:
        """Get information about a package from PyPI.
        
        Args:
            package_name: Name of the package
            
        Returns:
            PackageInfo object with package details
        """
        # Check cache first
        if package_name in self.package_cache:
            return self.package_cache[package_name]
        
        try:
            # Query PyPI API
            pypi_data = self._query_pypi(package_name)
            
            if pypi_data:
                # Extract version information
                versions = list(pypi_data.get('releases', {}).keys())
                # Simple string sorting (fallback)
                versions.sort(reverse=True)
                
                # Get latest version info
                latest_version = versions[0] if versions else 'unknown'
                
                # Extract requirements from latest version
                requirements = []
                latest_info = pypi_data.get('info', {})
                requires_dist = latest_info.get('requires_dist', [])
                if requires_dist:
                    requirements = [req for req in requires_dist if req]
                
                package_info = PackageInfo(
                    name=package_name,
                    version=latest_version,
                    requirements=requirements,
                    available_versions=versions,
                    is_available=True
                )
            else:
                package_info = PackageInfo(
                    name=package_name,
                    version='unknown',
                    requirements=[],
                    available_versions=[],
                    is_available=False
                )
            
            # Cache the result
            self.package_cache[package_name] = package_info
            return package_info
            
        except Exception as e:
            self.logger.debug(f"Failed to get info for {package_name}: {e}")
            package_info = PackageInfo(
                name=package_name,
                version='unknown',
                requirements=[],
                available_versions=[],
                is_available=False
            )
            self.package_cache[package_name] = package_info
            return package_info
    
    def _query_pypi(self, package_name: str) -> Optional[Dict]:
        """Query PyPI API for package information.
        
        Args:
            package_name: Name of the package
            
        Returns:
            PyPI API response data or None if failed
        """
        # Check cache first
        if package_name in self.pypi_cache:
            return self.pypi_cache[package_name]
        
        try:
            url = f"https://pypi.org/pypi/{package_name}/json"
            
            with urllib.request.urlopen(url, timeout=10) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode())
                    self.pypi_cache[package_name] = data
                    return data
                    
        except (urllib.error.URLError, urllib.error.HTTPError,
                json.JSONDecodeError) as e:
            self.logger.debug(f"PyPI query failed for {package_name}: {e}")
        
        return None
    
    def _detect_conflicts(self, requirements: List[str]
                          ) -> List[DependencyConflict]:
        """Detect version conflicts in requirements.
        
        Args:
            requirements: List of requirement strings
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        package_requirements: Dict[str, List[SimpleRequirement]] = {}
        
        # Group requirements by package name
        for req_str in requirements:
            try:
                req = SimpleRequirement(req_str)
                package_name = req.name.lower()
                
                if package_name not in package_requirements:
                    package_requirements[package_name] = []
                package_requirements[package_name].append(req)
                
            except Exception as e:
                self.logger.debug(f"Failed to parse requirement "
                                  f"{req_str}: {e}")
                continue
        
        # Check for conflicts within each package
        for package_name, reqs in package_requirements.items():
            if len(reqs) > 1:
                # Multiple requirements for the same package
                conflict = self._analyze_package_conflicts(package_name, reqs)
                if conflict:
                    conflicts.append(conflict)
        
        return conflicts
    
    def _analyze_package_conflicts(self, package_name: str,
                                   reqs: List[SimpleRequirement]
                                   ) -> Optional[DependencyConflict]:
        """Analyze conflicts for a specific package.
        
        Args:
            package_name: Name of the package
            reqs: List of requirements for this package
            
        Returns:
            DependencyConflict if conflicts found, None otherwise
        """
        if len(reqs) <= 1:
            return None
        
        # Get package info
        package_info = self._get_package_info(package_name)
        
        if not package_info.is_available:
            return DependencyConflict(
                package=package_name,
                conflicting_requirements=[req.original for req in reqs],
                suggested_resolution="Package not available on PyPI",
                severity="critical"
            )
        
        # Simple conflict detection - if we have different version requirements
        version_requirements = [req for req in reqs
                                if req.operator and req.version]
        
        if len(version_requirements) > 1:
            # Check for obvious conflicts (different exact versions)
            exact_versions = [req.version for req in version_requirements
                              if req.operator == '==']
            
            if len(set(exact_versions)) > 1:
                # Multiple different exact versions - definite conflict
                suggested_resolution = self._suggest_resolution(
                    package_name, reqs, package_info)
                
                severity = "high" if len(reqs) > 2 else "medium"
                
                return DependencyConflict(
                    package=package_name,
                    conflicting_requirements=[req.original for req in reqs],
                    suggested_resolution=suggested_resolution,
                    severity=severity
                )
        
        return None
    
    def _suggest_resolution(self, package_name: str,
                            reqs: List[SimpleRequirement],
                            package_info: PackageInfo) -> str:
        """Suggest a resolution for conflicting requirements.
        
        Args:
            package_name: Name of the package
            reqs: Conflicting requirements
            package_info: Package information
            
        Returns:
            Suggested resolution string
        """
        try:
            # Simple suggestion based on latest version
            if package_info.available_versions:
                latest_version = package_info.available_versions[0]
                return f"Use {package_name}=={latest_version}"
            else:
                return (f"Consider relaxing version constraints or use "
                        f"{package_name} latest version")
                
        except Exception:
            # Fallback suggestion
            return (f"Manually resolve version conflict for {package_name} "
                    f"by choosing compatible versions")
    
    def _generate_suggestions(self, requirements: List[str],
                              conflicts: List[DependencyConflict]
                              ) -> List[str]:
        """Generate general suggestions for improving requirements.
        
        Args:
            requirements: List of requirement strings
            conflicts: List of detected conflicts
            
        Returns:
            List of suggestion strings
        """
        suggestions = []
        
        # Count packages without version constraints
        unconstrained_count = 0
        for req_str in requirements:
            try:
                req = SimpleRequirement(req_str)
                if not req.operator:
                    unconstrained_count += 1
            except Exception:
                continue
        
        if unconstrained_count > len(requirements) * 0.3:
            suggestions.append(
                f"Consider adding version constraints to "
                f"{unconstrained_count} "
                f"packages to ensure reproducible builds"
            )
        
        if conflicts:
            suggestions.append(
                f"Resolve {len(conflicts)} dependency conflicts before "
                f"installation"
            )
        
        # Check for outdated packages
        outdated_packages = self._check_outdated_packages(requirements)
        if outdated_packages:
            suggestions.append(
                f"Consider updating {len(outdated_packages)} packages to "
                f"their latest versions"
            )
        
        return suggestions
    
    def _check_outdated_packages(self, requirements: List[str]) -> List[str]:
        """Check for packages that have newer versions available.
        
        Args:
            requirements: List of requirement strings
            
        Returns:
            List of outdated package names
        """
        outdated = []
        
        for req_str in requirements:
            try:
                req = SimpleRequirement(req_str)
                package_info = self._get_package_info(req.name)
                
                if not package_info.is_available:
                    continue
                
                # Check if there's a specific version requirement
                if req.operator == '==' and req.version:
                    current_version = req.version
                    latest_version = (package_info.available_versions[0]
                                      if package_info.available_versions
                                      else None)
                    
                    if latest_version and latest_version != current_version:
                        # Simple string comparison as fallback
                        if latest_version != current_version:
                            outdated.append(req.name)
                            
            except Exception:
                continue
        
        return outdated
    
    def create_dependency_tree(self, requirements: List[str],
                               max_depth: int = 3) -> Dict:
        """Create a dependency tree for the given requirements.
        
        Args:
            requirements: List of requirement strings
            max_depth: Maximum depth to traverse
            
        Returns:
            Dictionary representing the dependency tree
        """
        self.logger.info("Creating dependency tree...")
        
        tree = {
            'root': {
                'name': 'root',
                'version': 'N/A',
                'dependencies': {}
            }
        }
        
        # Process each top-level requirement
        for req_str in requirements:
            try:
                req = SimpleRequirement(req_str)
                self._build_dependency_subtree(
                    tree['root']['dependencies'],
                    req.name,
                    max_depth,
                    set()  # visited packages to avoid cycles
                )
            except Exception as e:
                self.logger.debug(f"Failed to process {req_str}: {e}")
                continue
        
        return tree
    
    def _build_dependency_subtree(self, parent_deps: Dict, package_name: str,
                                  remaining_depth: int, visited: Set[str]):
        """Recursively build dependency subtree.
        
        Args:
            parent_deps: Parent dependencies dictionary
            package_name: Name of current package
            remaining_depth: Remaining depth to traverse
            visited: Set of already visited packages
        """
        if remaining_depth <= 0 or package_name in visited:
            return
        
        visited.add(package_name)
        package_info = self._get_package_info(package_name)
        
        parent_deps[package_name] = {
            'name': package_name,
            'version': package_info.version,
            'available': package_info.is_available,
            'dependencies': {}
        }
        
        # Process dependencies of this package
        if package_info.is_available and package_info.requirements:
            for dep_req_str in package_info.requirements:
                try:
                    dep_req = SimpleRequirement(dep_req_str)
                    self._build_dependency_subtree(
                        parent_deps[package_name]['dependencies'],
                        dep_req.name,
                        remaining_depth - 1,
                        # Create copy to allow different branches
                        visited.copy()
                    )
                except Exception:
                    continue
    
    def validate_installation_order(self, requirements: List[str]
                                    ) -> List[str]:
        """Determine optimal installation order for packages.
        
        Args:
            requirements: List of requirement strings
            
        Returns:
            List of packages in recommended installation order
        """
        self.logger.info("Determining installation order...")
        
        # Create dependency graph
        graph = {}
        for req_str in requirements:
            try:
                req = SimpleRequirement(req_str)
                package_info = self._get_package_info(req.name)
                
                deps = []
                if package_info.is_available and package_info.requirements:
                    for dep_req_str in package_info.requirements:
                        try:
                            dep_req = SimpleRequirement(dep_req_str)
                            deps.append(dep_req.name)
                        except Exception:
                            continue
                
                graph[req.name] = deps
                
            except Exception:
                continue
        
        # Topological sort to determine installation order
        return self._topological_sort(graph)
    
    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """Perform topological sort on dependency graph.
        
        Args:
            graph: Dependency graph
            
        Returns:
            Topologically sorted list of packages
        """
        # Calculate in-degrees
        in_degree = {node: 0 for node in graph}
        for node in graph:
            for dep in graph[node]:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        # Find nodes with no incoming edges
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            # Remove edges from this node
            for dep in graph.get(node, []):
                if dep in in_degree:
                    in_degree[dep] -= 1
                    if in_degree[dep] == 0:
                        queue.append(dep)
        
        # Check for cycles
        if len(result) != len(graph):
            self.logger.warning("Circular dependencies detected")
            # Return remaining nodes in arbitrary order
            remaining = [node for node in graph if node not in result]
            result.extend(remaining)
        
        return result
    
    def generate_resolution_report(self, requirements_path: Path) -> str:
        """Generate a comprehensive dependency resolution report.
        
        Args:
            requirements_path: Path to requirements.txt file
            
        Returns:
            Formatted report string
        """
        analysis = self.analyze_requirements_file(requirements_path)
        
        if 'error' in analysis:
            return f"Error analyzing requirements: {analysis['error']}"
        
        report_lines = [
            "=" * 60,
            "DEPENDENCY RESOLUTION REPORT",
            "=" * 60,
            "",
            f"Requirements File: {requirements_path}",
            f"Total Packages: {analysis['total_packages']}",
            f"Valid Packages: {len(analysis['valid_packages'])}",
            f"Invalid Packages: {len(analysis['invalid_packages'])}",
            f"Conflicts: {len(analysis['conflicts'])}",
            "",
        ]
        
        # Add conflicts section
        if analysis['conflicts']:
            report_lines.extend([
                "CONFLICTS DETECTED:",
                "-" * 20,
            ])
            for conflict in analysis['conflicts']:
                report_lines.extend([
                    f"Package: {conflict['package']}",
                    f"Severity: {conflict['severity']}",
                    "Conflicting Requirements:",
                ])
                for req in conflict['conflicting_requirements']:
                    report_lines.append(f"  - {req}")
                if conflict['suggested_resolution']:
                    resolution = conflict['suggested_resolution']
                    report_lines.append(f"Suggested Resolution: {resolution}")
                report_lines.append("")
        
        # Add invalid packages section
        if analysis['invalid_packages']:
            report_lines.extend([
                "INVALID PACKAGES:",
                "-" * 17,
            ])
            for pkg in analysis['invalid_packages']:
                report_lines.extend([
                    f"Package: {pkg['name']}",
                    f"Reason: {pkg['reason']}",
                    "",
                ])
        
        # Add suggestions section
        if analysis['suggestions']:
            report_lines.extend([
                "SUGGESTIONS:",
                "-" * 12,
            ])
            for suggestion in analysis['suggestions']:
                report_lines.append(f"- {suggestion}")
            report_lines.append("")
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)