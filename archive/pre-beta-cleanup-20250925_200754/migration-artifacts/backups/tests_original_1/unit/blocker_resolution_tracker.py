#!/usr/bin/env python3
"""
Blocker Resolution Tracking System
Comprehensive monitoring and progress tracking for planned resolution blockers
Generated: September 2, 2025
"""

import datetime
import json
import os
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class BlockerStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Priority(Enum):
    CRITICAL = "🔴 CRITICAL"
    HIGH = "🟡 HIGH"
    MEDIUM = "🟢 MEDIUM"
    LOW = "🔵 LOW"

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class BlockerAction:
    """Individual action within a blocker resolution"""
    action_id: str
    description: str
    assigned_to: str
    status: BlockerStatus
    start_date: Optional[str] = None
    completion_date: Optional[str] = None
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    dependencies: List[str] = None
    notes: str = ""

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class BlockerMetrics:
    """Metrics tracking for blocker resolution"""
    tests_affected: int = 0
    tests_passing: int = 0
    coverage_improvement: float = 0.0
    performance_impact: float = 0.0
    installation_time: Optional[float] = None
    execution_time: Optional[float] = None

@dataclass
class BlockerTracker:
    """Main blocker tracking entity"""
    blocker_id: str
    title: str
    category: str
    priority: Priority
    status: BlockerStatus
    description: str
    root_cause: str
    impact: str
    owner: str
    created_date: str
    estimated_completion: str
    actual_completion: Optional[str] = None
    progress_percentage: float = 0.0
    actions: List[BlockerAction] = None
    metrics: BlockerMetrics = None
    current_obstacles: List[str] = None
    next_steps: List[str] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM
    dependencies: List[str] = None
    success_criteria: List[str] = None
    lessons_learned: List[str] = None

    def __post_init__(self):
        if self.actions is None:
            self.actions = []
        if self.metrics is None:
            self.metrics = BlockerMetrics()
        if self.current_obstacles is None:
            self.current_obstacles = []
        if self.next_steps is None:
            self.next_steps = []
        if self.dependencies is None:
            self.dependencies = []
        if self.success_criteria is None:
            self.success_criteria = []
        if self.lessons_learned is None:
            self.lessons_learned = []

class BlockerResolutionTracker:
    """Main tracking system for all blocker resolutions"""
    
    def __init__(self, data_file: str = "blocker_resolution_tracking.json"):
        self.data_file = data_file
        self.blockers: Dict[str, BlockerTracker] = {}
        self.load_data()
        self.initialize_default_blockers()

    def load_data(self):
        """Load existing tracking data"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for blocker_id, blocker_data in data.get('blockers', {}).items():
                        # Convert actions
                        actions = [BlockerAction(**action) for action in blocker_data.get('actions', [])]
                        blocker_data['actions'] = actions
                        
                        # Convert metrics
                        metrics_data = blocker_data.get('metrics', {})
                        blocker_data['metrics'] = BlockerMetrics(**metrics_data)
                        
                        # Convert enums
                        blocker_data['priority'] = Priority(blocker_data['priority'])
                        blocker_data['status'] = BlockerStatus(blocker_data['status'])
                        blocker_data['risk_level'] = RiskLevel(blocker_data['risk_level'])
                        
                        self.blockers[blocker_id] = BlockerTracker(**blocker_data)
            except Exception as e:
                print(f"Error loading tracking data: {e}")

    def save_data(self):
        """Save tracking data to file"""
        try:
            data = {
                'last_updated': datetime.datetime.now().isoformat(),
                'blockers': {}
            }
            
            for blocker_id, blocker in self.blockers.items():
                blocker_dict = asdict(blocker)
                # Convert enums to strings
                blocker_dict['priority'] = blocker.priority.value
                blocker_dict['status'] = blocker.status.value
                blocker_dict['risk_level'] = blocker.risk_level.value
                data['blockers'][blocker_id] = blocker_dict
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Error saving tracking data: {e}")

    def initialize_default_blockers(self):
        """Initialize default blockers if not already present"""
        default_blockers = [
            {
                'blocker_id': 'VD-001',
                'title': 'Visualization Dependencies',
                'category': 'Dependencies',
                'priority': Priority.CRITICAL,
                'status': BlockerStatus.NOT_STARTED,
                'description': 'Missing matplotlib and numpy packages causing test failures',
                'root_cause': 'Visualization packages not included in core test requirements',
                'impact': 'Advanced analysis features untested, 12+ test failures',
                'owner': 'DevOps Team',
                'created_date': '2025-09-02',
                'estimated_completion': '2025-09-05',
                'success_criteria': [
                    'All visualization packages installed without conflicts',
                    '12+ failing tests now pass',
                    'Visualization test markers properly configured',
                    'No regression in existing test performance'
                ],
                'actions': [
                    BlockerAction(
                        'VD-001-A1',
                        'Update requirements-test.txt with visualization dependencies',
                        'DevOps Engineer',
                        BlockerStatus.NOT_STARTED,
                        estimated_hours=2.0
                    ),
                    BlockerAction(
                        'VD-001-A2',
                        'Install and validate package compatibility',
                        'DevOps Engineer',
                        BlockerStatus.NOT_STARTED,
                        estimated_hours=4.0,
                        dependencies=['VD-001-A1']
                    ),
                    BlockerAction(
                        'VD-001-A3',
                        'Execute affected visualization tests',
                        'QA Engineer',
                        BlockerStatus.NOT_STARTED,
                        estimated_hours=8.0,
                        dependencies=['VD-001-A2']
                    )
                ]
            },
            {
                'blocker_id': 'LC-001',
                'title': 'Legacy Component Dependencies',
                'category': 'Technical Debt',
                'priority': Priority.HIGH,
                'status': BlockerStatus.NOT_STARTED,
                'description': 'Outdated interface compatibility affecting test coverage',
                'root_cause': 'Technical debt from deprecated APIs and frameworks',
                'impact': '35% coverage on legacy components, modernization decisions needed',
                'owner': 'Engineering Team',
                'created_date': '2025-09-02',
                'estimated_completion': '2025-09-30',
                'success_criteria': [
                    '100% legacy components classified and assessed',
                    'Modernization plan for critical components approved',
                    'Deprecation timeline for low-value components established',
                    'Test coverage for legacy components improved to >75%'
                ]
            },
            {
                'blocker_id': 'AC-001',
                'title': 'Accessibility Compliance (WCAG 2.1 AA)',
                'category': 'Compliance',
                'priority': Priority.HIGH,
                'status': BlockerStatus.NOT_STARTED,
                'description': 'Low accessibility coverage requiring comprehensive implementation',
                'root_cause': 'No automated accessibility testing framework established',
                'impact': 'Regulatory compliance gap, potential legal/business risk',
                'owner': 'UI/UX Team',
                'created_date': '2025-09-02',
                'estimated_completion': '2026-06-30',
                'success_criteria': [
                    'Accessibility coverage increased from 6.4% to 95%',
                    'WCAG 2.1 AA compliance achieved',
                    'Automated accessibility testing in CI/CD',
                    'Third-party accessibility audit passed'
                ]
            },
            {
                'blocker_id': 'PT-001',
                'title': 'Performance Regression Testing',
                'category': 'Quality Assurance',
                'priority': Priority.HIGH,
                'status': BlockerStatus.NOT_STARTED,
                'description': 'Insufficient automated performance monitoring',
                'root_cause': 'No systematic performance monitoring in CI/CD pipeline',
                'impact': 'Performance regressions may go undetected',
                'owner': 'DevOps Team',
                'created_date': '2025-09-02',
                'estimated_completion': '2025-12-31',
                'success_criteria': [
                    'Performance coverage increased from 24% to 85%',
                    'CI/CD performance gates implemented',
                    'Cross-platform performance baselines established',
                    'Automated regression detection active'
                ]
            }
        ]

        for blocker_data in default_blockers:
            if blocker_data['blocker_id'] not in self.blockers:
                # Convert actions if present
                if 'actions' in blocker_data:
                    actions = blocker_data['actions']
                    blocker_data['actions'] = actions
                
                blocker = BlockerTracker(**blocker_data)
                self.blockers[blocker_data['blocker_id']] = blocker

    def add_blocker(self, blocker: BlockerTracker):
        """Add a new blocker to track"""
        self.blockers[blocker.blocker_id] = blocker
        self.save_data()

    def update_blocker_status(self, blocker_id: str, status: BlockerStatus, notes: str = ""):
        """Update blocker status"""
        if blocker_id in self.blockers:
            self.blockers[blocker_id].status = status
            if status == BlockerStatus.COMPLETED:
                self.blockers[blocker_id].actual_completion = datetime.datetime.now().isoformat()
                self.blockers[blocker_id].progress_percentage = 100.0
            if notes:
                self.add_progress_note(blocker_id, notes)
            self.save_data()

    def update_action_status(self, blocker_id: str, action_id: str, status: BlockerStatus, 
                           actual_hours: float = 0.0, notes: str = ""):
        """Update individual action status"""
        if blocker_id in self.blockers:
            for action in self.blockers[blocker_id].actions:
                if action.action_id == action_id:
                    action.status = status
                    if actual_hours > 0:
                        action.actual_hours = actual_hours
                    if status == BlockerStatus.COMPLETED:
                        action.completion_date = datetime.datetime.now().isoformat()
                    if notes:
                        action.notes = notes
                    break
            
            # Recalculate progress
            self.calculate_progress(blocker_id)
            self.save_data()

    def calculate_progress(self, blocker_id: str):
        """Calculate overall progress for a blocker"""
        if blocker_id in self.blockers:
            blocker = self.blockers[blocker_id]
            if not blocker.actions:
                return
            
            completed_actions = sum(1 for action in blocker.actions 
                                  if action.status == BlockerStatus.COMPLETED)
            total_actions = len(blocker.actions)
            
            blocker.progress_percentage = (completed_actions / total_actions) * 100

    def add_obstacle(self, blocker_id: str, obstacle: str):
        """Add current obstacle to blocker"""
        if blocker_id in self.blockers:
            self.blockers[blocker_id].current_obstacles.append(obstacle)
            self.save_data()

    def add_next_step(self, blocker_id: str, next_step: str):
        """Add next step to blocker"""
        if blocker_id in self.blockers:
            self.blockers[blocker_id].next_steps.append(next_step)
            self.save_data()

    def add_lesson_learned(self, blocker_id: str, lesson: str):
        """Add lesson learned to blocker"""
        if blocker_id in self.blockers:
            self.blockers[blocker_id].lessons_learned.append(lesson)
            self.save_data()

    def add_progress_note(self, blocker_id: str, note: str):
        """Add a timestamped progress note"""
        timestamp = datetime.datetime.now().isoformat()
        note_with_timestamp = f"[{timestamp}] {note}"
        self.add_next_step(blocker_id, note_with_timestamp)

    def get_status_summary(self) -> Dict[str, Any]:
        """Get overall status summary"""
        total_blockers = len(self.blockers)
        status_counts = {}
        priority_counts = {}
        
        for blocker in self.blockers.values():
            status = blocker.status.value
            priority = blocker.priority.value
            
            status_counts[status] = status_counts.get(status, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        overall_progress = sum(blocker.progress_percentage for blocker in self.blockers.values()) / total_blockers if total_blockers > 0 else 0

        return {
            'total_blockers': total_blockers,
            'overall_progress': round(overall_progress, 1),
            'status_distribution': status_counts,
            'priority_distribution': priority_counts,
            'critical_count': sum(1 for b in self.blockers.values() if b.priority == Priority.CRITICAL),
            'overdue_count': self.get_overdue_count(),
            'last_updated': datetime.datetime.now().isoformat()
        }

    def get_overdue_count(self) -> int:
        """Count overdue blockers"""
        today = datetime.datetime.now().date()
        overdue = 0
        
        for blocker in self.blockers.values():
            if blocker.status not in [BlockerStatus.COMPLETED, BlockerStatus.CANCELLED]:
                try:
                    estimated_date = datetime.datetime.fromisoformat(blocker.estimated_completion).date()
                    if estimated_date < today:
                        overdue += 1
                except:
                    pass
        
        return overdue

    def generate_daily_report(self) -> str:
        """Generate daily progress report"""
        summary = self.get_status_summary()
        
        report = f"""
# DAILY BLOCKER RESOLUTION REPORT
**Date:** {datetime.datetime.now().strftime('%Y-%m-%d')}
**Overall Progress:** {summary['overall_progress']}%

## SUMMARY METRICS
- **Total Blockers:** {summary['total_blockers']}
- **Critical Blockers:** {summary['critical_count']}
- **Overdue Blockers:** {summary['overdue_count']}

## STATUS BREAKDOWN
"""
        
        for status, count in summary['status_distribution'].items():
            report += f"- **{status}:** {count}\n"

        report += "\n## BLOCKER DETAILS\n"
        
        for blocker_id, blocker in self.blockers.items():
            report += f"\n### {blocker_id}: {blocker.title}\n"
            report += f"- **Status:** {blocker.status.value}\n"
            report += f"- **Progress:** {blocker.progress_percentage}%\n"
            report += f"- **Owner:** {blocker.owner}\n"
            report += f"- **Target Completion:** {blocker.estimated_completion}\n"
            
            if blocker.current_obstacles:
                report += f"- **Current Obstacles:** {', '.join(blocker.current_obstacles[-3:])}\n"
            
            if blocker.next_steps:
                report += f"- **Next Steps:** {', '.join(blocker.next_steps[-3:])}\n"

        return report

    def generate_weekly_report(self) -> str:
        """Generate weekly progress report"""
        report = self.generate_daily_report()
        report = report.replace("DAILY", "WEEKLY")
        
        # Add lessons learned section
        report += "\n## LESSONS LEARNED THIS WEEK\n"
        for blocker_id, blocker in self.blockers.items():
            if blocker.lessons_learned:
                report += f"\n### {blocker_id}: {blocker.title}\n"
                for lesson in blocker.lessons_learned[-5:]:  # Last 5 lessons
                    report += f"- {lesson}\n"
        
        return report

def main():
    """Demo usage of the tracking system"""
    tracker = BlockerResolutionTracker()
    
    # Example: Update a blocker status
    tracker.update_blocker_status('VD-001', BlockerStatus.IN_PROGRESS, 
                                  "Started working on visualization dependencies")
    
    # Example: Update an action
    tracker.update_action_status('VD-001', 'VD-001-A1', BlockerStatus.COMPLETED, 
                                 actual_hours=1.5, notes="Requirements file updated successfully")
    
    # Example: Add obstacle
    tracker.add_obstacle('VD-001', "Package version conflicts detected")
    
    # Example: Add next step
    tracker.add_next_step('VD-001', "Resolve matplotlib version compatibility issue")
    
    # Generate reports
    daily_report = tracker.generate_daily_report()
    print(daily_report)
    
    # Save the tracking data
    tracker.save_data()
    
    print(f"\nTracking data saved to: {tracker.data_file}")

if __name__ == "__main__":
    main()