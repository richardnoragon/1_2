#!/usr/bin/env python3
"""
Simple Blocker Dependencies Analysis (No Matplotlib)
Text-based dependency analysis and critical path calculation
Generated: September 2, 2025
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Set


class SimpleDependencyAnalyzer:
    """Simple dependency analyzer without visualization dependencies"""
    
    def __init__(self, tracker_data_file: str = "blocker_resolution_tracking.json"):
        self.data_file = tracker_data_file
        self.blockers = {}
        self.load_data()

    def load_data(self):
        """Load blocker tracking data or create default"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.blockers = data.get('blockers', {})
        except FileNotFoundError:
            print(f"Warning: {self.data_file} not found. Using default dependencies.")
            self.create_default_dependencies()

    def create_default_dependencies(self):
        """Create default dependency structure"""
        self.blockers = {
            'VD-001': {
                'title': 'Visualization Dependencies',
                'priority': '🔴 CRITICAL',
                'estimated_completion': '2025-09-05',
                'dependencies': [],
                'blocking': ['FT-001', 'CP-001'],
                'status': 'COMPLETED'
            },
            'LC-001': {
                'title': 'Legacy Component Dependencies',
                'priority': '🟡 HIGH',
                'estimated_completion': '2025-09-30',
                'dependencies': [],
                'blocking': ['PT-001'],
                'status': 'NOT_STARTED'
            },
            'FT-001': {
                'title': 'Failed Test Remediation',
                'priority': '🟡 MEDIUM',
                'estimated_completion': '2025-09-12',
                'dependencies': ['VD-001'],
                'blocking': ['CP-001'],
                'status': 'NOT_STARTED'
            },
            'CP-001': {
                'title': 'Cross-Platform Compatibility',
                'priority': '🟡 MEDIUM',
                'estimated_completion': '2025-09-16',
                'dependencies': ['VD-001', 'FT-001'],
                'blocking': [],
                'status': 'NOT_STARTED'
            },
            'AC-001': {
                'title': 'Accessibility Compliance',
                'priority': '🟡 HIGH',
                'estimated_completion': '2026-06-30',
                'dependencies': [],
                'blocking': ['PT-001'],
                'status': 'NOT_STARTED'
            },
            'PT-001': {
                'title': 'Performance Testing Framework',
                'priority': '🟡 HIGH',
                'estimated_completion': '2025-12-31',
                'dependencies': ['LC-001', 'AC-001'],
                'blocking': [],
                'status': 'NOT_STARTED'
            }
        }

    def find_critical_path(self) -> List[str]:
        """Find critical path using topological sort"""
        # Build dependency graph
        in_degree = {}
        graph = {}
        
        for blocker_id in self.blockers:
            in_degree[blocker_id] = 0
            graph[blocker_id] = []
        
        # Add edges
        for blocker_id, blocker in self.blockers.items():
            dependencies = blocker.get('dependencies', [])
            for dep in dependencies:
                if dep in self.blockers:
                    graph[dep].append(blocker_id)
                    in_degree[blocker_id] += 1
        
        # Topological sort
        queue = [blocker for blocker, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result

    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies using DFS"""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node, path):
            if node in rec_stack:
                # Found cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
                
            visited.add(node)
            rec_stack.add(node)
            
            dependencies = self.blockers.get(node, {}).get('dependencies', [])
            for dep in dependencies:
                if dep in self.blockers:
                    dfs(dep, path + [node])
            
            rec_stack.remove(node)
        
        for blocker_id in self.blockers:
            if blocker_id not in visited:
                dfs(blocker_id, [])
        
        return cycles

    def calculate_earliest_completion(self) -> Dict[str, datetime]:
        """Calculate earliest completion time for each blocker"""
        completion_times = {}
        critical_path = self.find_critical_path()
        
        for blocker_id in critical_path:
            blocker = self.blockers[blocker_id]
            dependencies = blocker.get('dependencies', [])
            
            if not dependencies:
                # No dependencies, use estimated completion
                completion_times[blocker_id] = datetime.fromisoformat(
                    blocker.get('estimated_completion', '2025-09-02')
                )
            else:
                # Complete after all dependencies
                latest_dep_completion = datetime.now()
                for dep in dependencies:
                    if dep in completion_times:
                        dep_completion = completion_times[dep]
                        if dep_completion > latest_dep_completion:
                            latest_dep_completion = dep_completion
                
                # Add duration for this blocker
                estimated_completion = datetime.fromisoformat(
                    blocker.get('estimated_completion', '2025-09-02')
                )
                completion_times[blocker_id] = max(latest_dep_completion, estimated_completion)
        
        return completion_times

    def generate_text_gantt(self) -> str:
        """Generate text-based Gantt chart"""
        critical_path = self.find_critical_path()
        completion_times = self.calculate_earliest_completion()
        
        gantt = "\n# TEXT-BASED GANTT CHART\n\n"
        gantt += "Timeline (Weeks from Sept 2, 2025):\n"
        gantt += "0----5----10---15---20---25---30---35---40---45---50\n"
        
        project_start = datetime(2025, 9, 2)
        
        for blocker_id in critical_path:
            blocker = self.blockers[blocker_id]
            completion_date = completion_times.get(blocker_id, project_start)
            weeks_from_start = (completion_date - project_start).days // 7
            
            # Create timeline bar
            bar = ['-'] * 50
            for i in range(min(weeks_from_start, 49)):
                bar[i] = '█'
            
            status_icon = {
                'COMPLETED': '✅',
                'IN_PROGRESS': '🔄',
                'NOT_STARTED': '⏸️',
                'BLOCKED': '🚫'
            }.get(blocker.get('status', 'NOT_STARTED'), '❓')
            
            gantt += f"{blocker_id}: {''.join(bar)} {status_icon}\n"
            gantt += f"        {blocker.get('title', '')[:40]}...\n\n"
        
        return gantt

    def generate_analysis_report(self) -> str:
        """Generate comprehensive text-based analysis"""
        critical_path = self.find_critical_path()
        circular_deps = self.detect_circular_dependencies()
        completion_times = self.calculate_earliest_completion()
        
        report = f"""
# BLOCKER DEPENDENCIES ANALYSIS REPORT
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## EXECUTIVE SUMMARY
- **Total Blockers:** {len(self.blockers)}
- **Critical Path Length:** {len(critical_path)} blockers
- **Circular Dependencies:** {len(circular_deps)} detected
- **Project End Date:** {max(completion_times.values()).strftime('%Y-%m-%d') if completion_times else 'TBD'}

## CRITICAL PATH ANALYSIS
**Critical Path:** {' → '.join(critical_path)}

### Critical Path Details:
"""
        
        total_duration = 0
        for i, blocker_id in enumerate(critical_path):
            blocker = self.blockers.get(blocker_id, {})
            completion_date = completion_times.get(blocker_id, datetime.now())
            
            if i == 0:
                start_date = datetime(2025, 9, 2)
            else:
                prev_blocker = critical_path[i-1]
                start_date = completion_times.get(prev_blocker, datetime.now())
            
            duration = (completion_date - start_date).days
            total_duration += duration
            
            status = blocker.get('status', 'NOT_STARTED')
            status_icon = {
                'COMPLETED': '✅',
                'IN_PROGRESS': '🔄',
                'NOT_STARTED': '⏸️',
                'BLOCKED': '🚫'
            }.get(status, '❓')
            
            report += f"{i+1}. **{blocker_id}** {status_icon}: {blocker.get('title', '')}\n"
            report += f"   - Start: {start_date.strftime('%Y-%m-%d')}\n"
            report += f"   - End: {completion_date.strftime('%Y-%m-%d')}\n"
            report += f"   - Duration: {duration} days\n"
            report += f"   - Priority: {blocker.get('priority', 'Unknown')}\n"
            report += f"   - Status: {status}\n\n"
        
        report += f"**Total Critical Path Duration:** {total_duration} days\n\n"

        # Circular dependencies
        if circular_deps:
            report += "## ⚠️  CIRCULAR DEPENDENCIES DETECTED\n\n"
            for i, cycle in enumerate(circular_deps):
                report += f"**Cycle {i+1}:** {' → '.join(cycle)}\n"
            report += "\n**Action Required:** Resolve circular dependencies before proceeding.\n\n"
        else:
            report += "## ✅ NO CIRCULAR DEPENDENCIES\n\nDependency graph is acyclic and can be executed sequentially.\n\n"

        # Current status
        report += "## CURRENT STATUS OVERVIEW\n\n"
        status_counts = {}
        for blocker in self.blockers.values():
            status = blocker.get('status', 'NOT_STARTED')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in status_counts.items():
            icon = {
                'COMPLETED': '✅',
                'IN_PROGRESS': '🔄',
                'NOT_STARTED': '⏸️',
                'BLOCKED': '🚫'
            }.get(status, '❓')
            report += f"- **{status}** {icon}: {count} blockers\n"

        # Risk analysis
        report += "\n## RISK ANALYSIS\n\n"
        report += "### High-Risk Dependencies:\n"
        
        for blocker_id, blocker in self.blockers.items():
            blocking = blocker.get('blocking', [])
            if len(blocking) > 1:
                report += f"- **{blocker_id}** blocks {len(blocking)} other blockers: {', '.join(blocking)}\n"
        
        report += "\n### Dependency Bottlenecks:\n"
        
        for blocker_id, blocker in self.blockers.items():
            dependencies = blocker.get('dependencies', [])
            if len(dependencies) > 1:
                report += f"- **{blocker_id}** depends on {len(dependencies)} blockers: {', '.join(dependencies)}\n"

        # Parallel execution opportunities
        report += "\n## PARALLEL EXECUTION OPPORTUNITIES\n\n"
        independent_blockers = []
        for blocker_id, blocker in self.blockers.items():
            if not blocker.get('dependencies', []):
                independent_blockers.append(blocker_id)
        
        if independent_blockers:
            report += "**Independent Blockers** (can start immediately):\n"
            for blocker_id in independent_blockers:
                blocker = self.blockers.get(blocker_id, {})
                status = blocker.get('status', 'NOT_STARTED')
                icon = {
                    'COMPLETED': '✅',
                    'IN_PROGRESS': '🔄',
                    'NOT_STARTED': '⏸️',
                    'BLOCKED': '🚫'
                }.get(status, '❓')
                report += f"- {blocker_id} {icon}: {blocker.get('title', '')}\n"
        
        # Add text gantt chart
        report += self.generate_text_gantt()
        
        # Next actions
        report += "\n## IMMEDIATE NEXT ACTIONS\n\n"
        
        # Find next actionable blockers
        actionable = []
        for blocker_id, blocker in self.blockers.items():
            if blocker.get('status') == 'NOT_STARTED':
                dependencies = blocker.get('dependencies', [])
                can_start = True
                for dep in dependencies:
                    dep_status = self.blockers.get(dep, {}).get('status', 'NOT_STARTED')
                    if dep_status != 'COMPLETED':
                        can_start = False
                        break
                
                if can_start:
                    actionable.append(blocker_id)
        
        if actionable:
            report += "**Ready to Start:**\n"
            for blocker_id in actionable:
                blocker = self.blockers.get(blocker_id, {})
                report += f"1. **{blocker_id}**: {blocker.get('title', '')}\n"
                report += f"   - Priority: {blocker.get('priority', 'Unknown')}\n"
                report += f"   - Target: {blocker.get('estimated_completion', 'TBD')}\n"
                report += f"   - Command: `./manage-blockers-fixed.ps1 update {blocker_id} -Status IN_PROGRESS`\n\n"
        
        return report

def main():
    """Generate dependency analysis"""
    print("🔄 Generating blocker dependency analysis (text-based)...")
    
    analyzer = SimpleDependencyAnalyzer()
    
    # Generate report
    report = analyzer.generate_analysis_report()
    
    # Save report
    with open("blocker_dependency_analysis_simple.md", "w", encoding='utf-8') as f:
        f.write(report)
    
    print("📄 Dependency analysis report saved to: blocker_dependency_analysis_simple.md")
    print("\n" + "="*80)
    print(report)

if __name__ == "__main__":
    main()