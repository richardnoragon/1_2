#!/usr/bin/env python3
"""
Blocker Dependencies Mapping and Visualization
Generates dependency graphs and critical path analysis for blocker resolution
Generated: September 2, 2025
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


class BlockerDependencyMapper:
    """Maps and analyzes dependencies between blockers"""

    def __init__(
        self, tracker_data_file: str = "blocker_resolution_tracking.json"
    ):
        self.data_file = tracker_data_file
        self.blockers = {}
        self.dependency_graph = nx.DiGraph()
        self.load_data()
        self.build_dependency_graph()

    def load_data(self):
        """Load blocker tracking data"""
        try:
            with open(self.data_file, "r") as f:
                data = json.load(f)
                self.blockers = data.get("blockers", {})
        except FileNotFoundError:
            print(
                f"Warning: {self.data_file} not found. Using default dependencies."
            )
            self.create_default_dependencies()

    def create_default_dependencies(self):
        """Create default dependency structure"""
        self.blockers = {
            "VD-001": {
                "title": "Visualization Dependencies",
                "priority": "🔴 CRITICAL",
                "estimated_completion": "2025-09-05",
                "dependencies": [],
                "blocking": ["FT-001", "CP-001"],
            },
            "LC-001": {
                "title": "Legacy Component Dependencies",
                "priority": "🟡 HIGH",
                "estimated_completion": "2025-09-30",
                "dependencies": [],
                "blocking": ["PT-001"],
            },
            "FT-001": {
                "title": "Failed Test Remediation",
                "priority": "🟡 MEDIUM",
                "estimated_completion": "2025-09-12",
                "dependencies": ["VD-001"],
                "blocking": ["CP-001"],
            },
            "CP-001": {
                "title": "Cross-Platform Compatibility",
                "priority": "🟡 MEDIUM",
                "estimated_completion": "2025-09-16",
                "dependencies": ["VD-001", "FT-001"],
                "blocking": [],
            },
            "AC-001": {
                "title": "Accessibility Compliance",
                "priority": "🟡 HIGH",
                "estimated_completion": "2026-06-30",
                "dependencies": [],
                "blocking": ["PT-001"],
            },
            "PT-001": {
                "title": "Performance Testing Framework",
                "priority": "🟡 HIGH",
                "estimated_completion": "2025-12-31",
                "dependencies": ["LC-001", "AC-001"],
                "blocking": [],
            },
        }

    def build_dependency_graph(self):
        """Build networkx dependency graph"""
        # Add nodes
        for blocker_id, blocker in self.blockers.items():
            priority_weight = self.get_priority_weight(
                blocker.get("priority", "🟡 HIGH")
            )
            self.dependency_graph.add_node(
                blocker_id,
                title=blocker.get("title", ""),
                priority=blocker.get("priority", "🟡 HIGH"),
                weight=priority_weight,
                completion=blocker.get("estimated_completion", ""),
                status=blocker.get("status", "NOT_STARTED"),
            )

        # Add edges for dependencies
        for blocker_id, blocker in self.blockers.items():
            dependencies = blocker.get("dependencies", [])
            for dep in dependencies:
                if dep in self.blockers:
                    self.dependency_graph.add_edge(dep, blocker_id)

    def get_priority_weight(self, priority: str) -> int:
        """Convert priority to numeric weight"""
        weights = {"🔴 CRITICAL": 4, "🟡 HIGH": 3, "🟢 MEDIUM": 2, "🔵 LOW": 1}
        return weights.get(priority, 2)

    def find_critical_path(self) -> List[str]:
        """Find critical path through dependency graph"""
        try:
            # Find longest path (critical path)
            return nx.dag_longest_path(self.dependency_graph, weight="weight")
        except nx.NetworkXError:
            # If graph has cycles, use topological sort
            try:
                return list(nx.topological_sort(self.dependency_graph))
            except nx.NetworkXError:
                return list(self.blockers.keys())

    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies"""
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            return cycles
        except:
            return []

    def calculate_earliest_start_times(self) -> Dict[str, datetime]:
        """Calculate earliest start time for each blocker"""
        start_times = {}
        sorted_blockers = list(nx.topological_sort(self.dependency_graph))

        for blocker_id in sorted_blockers:
            dependencies = list(self.dependency_graph.predecessors(blocker_id))

            if not dependencies:
                # No dependencies, can start immediately
                start_times[blocker_id] = datetime.now()
            else:
                # Start after all dependencies complete
                latest_dependency_end = datetime.now()
                for dep in dependencies:
                    dep_completion = self.blockers[dep].get(
                        "estimated_completion", "2025-09-02"
                    )
                    dep_end = datetime.fromisoformat(dep_completion)
                    if dep_end > latest_dependency_end:
                        latest_dependency_end = dep_end

                start_times[blocker_id] = latest_dependency_end

        return start_times

    def generate_gantt_data(self) -> pd.DataFrame:
        """Generate Gantt chart data"""
        start_times = self.calculate_earliest_start_times()
        gantt_data = []

        for blocker_id, blocker in self.blockers.items():
            start_time = start_times.get(blocker_id, datetime.now())
            end_time = datetime.fromisoformat(
                blocker.get("estimated_completion", "2025-09-02")
            )
            duration = (end_time - start_time).days

            gantt_data.append(
                {
                    "Task": blocker_id,
                    "Title": blocker.get("title", ""),
                    "Start": start_time,
                    "End": end_time,
                    "Duration": max(duration, 1),  # Minimum 1 day
                    "Priority": blocker.get("priority", "🟡 HIGH"),
                    "Status": blocker.get("status", "NOT_STARTED"),
                }
            )

        return pd.DataFrame(gantt_data)

    def visualize_dependency_graph(
        self, output_file: str = "blocker_dependencies.png"
    ):
        """Create dependency graph visualization"""
        plt.figure(figsize=(14, 10))

        # Create layout
        pos = nx.spring_layout(self.dependency_graph, k=3, iterations=50)

        # Color mapping for priorities
        priority_colors = {
            "🔴 CRITICAL": "#FF4444",
            "🟡 HIGH": "#FFB800",
            "🟢 MEDIUM": "#28A745",
            "🔵 LOW": "#007BFF",
        }

        # Draw nodes
        for node in self.dependency_graph.nodes():
            priority = self.dependency_graph.nodes[node].get(
                "priority", "🟡 HIGH"
            )
            color = priority_colors.get(priority, "#28A745")

            nx.draw_networkx_nodes(
                self.dependency_graph,
                pos,
                nodelist=[node],
                node_color=color,
                node_size=1500,
                alpha=0.8,
            )

        # Draw edges
        nx.draw_networkx_edges(
            self.dependency_graph,
            pos,
            edge_color="gray",
            arrows=True,
            arrowsize=20,
            arrowstyle="->",
            alpha=0.6,
        )

        # Add labels
        labels = {}
        for node in self.dependency_graph.nodes():
            title = self.dependency_graph.nodes[node].get("title", "")
            labels[node] = f"{node}\n{title[:20]}..."

        nx.draw_networkx_labels(
            self.dependency_graph, pos, labels, font_size=8
        )

        # Create legend
        legend_elements = [
            mpatches.Patch(color="#FF4444", label="🔴 Critical"),
            mpatches.Patch(color="#FFB800", label="🟡 High"),
            mpatches.Patch(color="#28A745", label="🟢 Medium"),
            mpatches.Patch(color="#007BFF", label="🔵 Low"),
        ]
        plt.legend(handles=legend_elements, loc="upper right")

        plt.title(
            "Blocker Resolution Dependencies", fontsize=16, fontweight="bold"
        )
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        print(f"Dependency graph saved to: {output_file}")

    def create_gantt_chart(self, output_file: str = "blocker_gantt_chart.png"):
        """Create Gantt chart visualization"""
        df = self.generate_gantt_data()

        fig, ax = plt.subplots(figsize=(16, 8))

        # Color mapping
        priority_colors = {
            "🔴 CRITICAL": "#FF4444",
            "🟡 HIGH": "#FFB800",
            "🟢 MEDIUM": "#28A745",
            "🔵 LOW": "#007BFF",
        }

        status_patterns = {
            "NOT_STARTED": "",
            "IN_PROGRESS": "///",
            "BLOCKED": "xxx",
            "COMPLETED": "...",
            "CANCELLED": "---",
        }

        # Create bars
        y_pos = range(len(df))

        for i, (_, row) in enumerate(df.iterrows()):
            start_date = row["Start"]
            duration = row["Duration"]
            color = priority_colors.get(row["Priority"], "#28A745")
            pattern = status_patterns.get(row["Status"], "")

            # Calculate position relative to project start
            project_start = df["Start"].min()
            start_offset = (start_date - project_start).days

            bar = ax.barh(
                i,
                duration,
                left=start_offset,
                color=color,
                alpha=0.7,
                hatch=pattern,
                edgecolor="black",
            )

            # Add task label
            ax.text(
                start_offset + duration / 2,
                i,
                f"{row['Task']}\n{row['Title'][:15]}...",
                ha="center",
                va="center",
                fontsize=8,
                fontweight="bold",
            )

        # Customize chart
        ax.set_yticks(y_pos)
        ax.set_yticklabels([f"{row['Task']}" for _, row in df.iterrows()])
        ax.invert_yaxis()

        # Set x-axis to show dates
        project_start = df["Start"].min()
        project_end = df["End"].max()
        total_days = (project_end - project_start).days

        # Create date labels
        date_labels = []
        date_positions = []
        for i in range(0, total_days + 30, 30):  # Monthly intervals
            date = project_start + timedelta(days=i)
            date_labels.append(date.strftime("%Y-%m"))
            date_positions.append(i)

        ax.set_xticks(date_positions)
        ax.set_xticklabels(date_labels, rotation=45)
        ax.set_xlabel("Timeline (Months)")
        ax.set_ylabel("Blockers")
        ax.set_title(
            "Blocker Resolution Gantt Chart", fontsize=16, fontweight="bold"
        )

        # Add legend
        legend_elements = []
        for priority, color in priority_colors.items():
            legend_elements.append(mpatches.Patch(color=color, label=priority))

        ax.legend(handles=legend_elements, loc="upper right")

        # Add grid
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        print(f"Gantt chart saved to: {output_file}")

    def generate_dependency_report(self) -> str:
        """Generate comprehensive dependency analysis report"""
        critical_path = self.find_critical_path()
        circular_deps = self.detect_circular_dependencies()
        start_times = self.calculate_earliest_start_times()

        report = f"""
# BLOCKER DEPENDENCIES ANALYSIS REPORT
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## CRITICAL PATH ANALYSIS
**Critical Path:** {' → '.join(critical_path)}

The critical path represents the sequence of blockers that determines the minimum project duration.
Any delay in critical path blockers will delay the entire project completion.

### Critical Path Details:
"""

        total_critical_days = 0
        for i, blocker_id in enumerate(critical_path):
            blocker = self.blockers.get(blocker_id, {})
            start_time = start_times.get(blocker_id, datetime.now())
            end_time = datetime.fromisoformat(
                blocker.get("estimated_completion", "2025-09-02")
            )
            duration = (end_time - start_time).days
            total_critical_days += duration

            report += f"{i+1}. **{blocker_id}**: {blocker.get('title', '')}\n"
            report += f"   - Start: {start_time.strftime('%Y-%m-%d')}\n"
            report += f"   - End: {end_time.strftime('%Y-%m-%d')}\n"
            report += f"   - Duration: {duration} days\n"
            report += (
                f"   - Priority: {blocker.get('priority', 'Unknown')}\n\n"
            )

        report += (
            f"**Total Critical Path Duration:** {total_critical_days} days\n\n"
        )

        # Circular dependencies
        if circular_deps:
            report += "## ⚠️ CIRCULAR DEPENDENCIES DETECTED\n\n"
            for i, cycle in enumerate(circular_deps):
                report += (
                    f"**Cycle {i+1}:** {' → '.join(cycle + [cycle[0]])}\n"
                )
            report += "\n**Action Required:** Resolve circular dependencies before proceeding.\n\n"
        else:
            report += "## ✅ NO CIRCULAR DEPENDENCIES\n\nDependency graph is acyclic and can be executed sequentially.\n\n"

        # Risk analysis
        report += "## RISK ANALYSIS\n\n"
        report += "### High-Risk Dependencies:\n"

        for blocker_id, blocker in self.blockers.items():
            dependencies = blocker.get("dependencies", [])
            blocking = blocker.get("blocking", [])

            if len(blocking) > 2:  # Blocker affects many others
                report += f"- **{blocker_id}** blocks {len(blocking)} other blockers: {', '.join(blocking)}\n"

        report += "\n### Dependency Bottlenecks:\n"

        # Find nodes with high in-degree (many dependencies)
        for blocker_id in self.dependency_graph.nodes():
            in_degree = self.dependency_graph.in_degree(blocker_id)
            if in_degree > 1:
                predecessors = list(
                    self.dependency_graph.predecessors(blocker_id)
                )
                report += f"- **{blocker_id}** depends on {in_degree} blockers: {', '.join(predecessors)}\n"

        # Parallel execution opportunities
        report += "\n## PARALLEL EXECUTION OPPORTUNITIES\n\n"
        independent_blockers = []
        for blocker_id in self.dependency_graph.nodes():
            if self.dependency_graph.in_degree(blocker_id) == 0:
                independent_blockers.append(blocker_id)

        if independent_blockers:
            report += f"**Independent Blockers** (can start immediately):\n"
            for blocker_id in independent_blockers:
                blocker = self.blockers.get(blocker_id, {})
                report += f"- {blocker_id}: {blocker.get('title', '')}\n"

        # Resource optimization
        report += "\n## RESOURCE OPTIMIZATION RECOMMENDATIONS\n\n"
        report += "1. **Prioritize Critical Path:** Focus resources on critical path blockers first\n"
        report += "2. **Parallel Execution:** Start independent blockers simultaneously\n"
        report += "3. **Resource Allocation:** Assign senior team members to high-risk dependencies\n"
        report += "4. **Monitoring:** Implement daily check-ins for critical path progress\n"

        return report


def main():
    """Generate dependency analysis and visualizations"""
    print("🔄 Generating blocker dependency analysis...")

    mapper = BlockerDependencyMapper()

    # Generate visualizations
    try:
        mapper.visualize_dependency_graph()
        mapper.create_gantt_chart()
        print("✅ Visualizations generated successfully!")
    except ImportError:
        print("⚠️ Matplotlib not available. Skipping visualizations.")
        print("   Install matplotlib with: pip install matplotlib")
    except Exception as e:
        print(f"❌ Error generating visualizations: {e}")

    # Generate report
    report = mapper.generate_dependency_report()

    # Save report
    with open("blocker_dependency_analysis.md", "w") as f:
        f.write(report)

    print(
        "📄 Dependency analysis report saved to: blocker_dependency_analysis.md"
    )
    print("\n" + "=" * 60)
    print(report)


if __name__ == "__main__":
    main()
