"""
Phase 2B-DEBUG: Root Cause Analysis for SizeAnalyzer Memory Leak
Generated: September 9, 2025

This module provides focused root cause analysis for the specific memory leak
identified in SizeAnalyzer during sustained operations (10.08 MB/min leak rate).

**ROOT CAUSE ANALYSIS FOCUS:**
- Identify specific objects accumulating during sustained operations
- Analyze reference cycles and object retention patterns
- Profile memory usage patterns in realistic sustained scenarios
- Pinpoint exact leak vectors for targeted remediation

**METHODOLOGY:**
- Object lifecycle tracking during sustained operations
- Reference counting analysis for potential circular references
- Memory allocation pattern analysis with tracemalloc
- Garbage collection impact assessment
"""

import gc
import json
import os
import sys
import tempfile
import time
import tracemalloc
import weakref
from collections import defaultdict
from typing import Any, Dict, List, Tuple

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utilities.analysis.core.size_analyzer_logic import SizeAnalyzer


class SizeAnalyzerMemoryLeakRootCauseAnalyzer:
    """
    Comprehensive root cause analyzer for SizeAnalyzer memory leaks.
    
    This analyzer focuses specifically on identifying the exact source
    of memory leaks during sustained SizeAnalyzer operations.
    """
    
    def __init__(self):
        self.memory_snapshots = []
        self.object_growth_tracking = defaultdict(list)
        self.analyzer_instance_tracking = []
        self.operation_memory_deltas = []
        
    def create_test_dataset(self, size: str = "medium") -> str:
        """Create a test dataset for memory leak analysis."""
        test_dir = tempfile.mkdtemp(prefix="sizeanalyzer_debug_")
        
        if size == "small":
            file_count = 50
            content_size = 100
        elif size == "medium":
            file_count = 500
            content_size = 1000
        else:  # large
            file_count = 2000
            content_size = 5000
        
        # Create test files
        for i in range(file_count):
            file_path = os.path.join(test_dir, f"test_file_{i:04d}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Test content for file {i}\n" + "x" * content_size)
        
        # Create some subdirectories
        for i in range(10):
            subdir = os.path.join(test_dir, f"subdir_{i:02d}")
            os.makedirs(subdir, exist_ok=True)
            
            for j in range(5):
                file_path = os.path.join(subdir, f"sub_file_{j:02d}.txt")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Subdirectory content {i}-{j}\n" + "y" * content_size)
        
        return test_dir
    
    def take_memory_snapshot(self, label: str) -> Dict[str, Any]:
        """Take a comprehensive memory snapshot."""
        # Force garbage collection first
        gc.collect()
        
        # Get tracemalloc snapshot if available
        tracemalloc_snapshot = None
        if tracemalloc.is_tracing():
            tracemalloc_snapshot = tracemalloc.take_snapshot()
        
        # Get object counts by type
        object_counts = defaultdict(int)
        all_objects = gc.get_objects()
        
        for obj in all_objects:
            obj_type = type(obj).__name__
            object_counts[obj_type] += 1
        
        # Get memory info
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        snapshot = {
            'label': label,
            'timestamp': time.time(),
            'memory_rss': memory_info.rss,
            'memory_vms': memory_info.vms,
            'object_counts': dict(object_counts),
            'total_objects': len(all_objects),
            'garbage_count': len(gc.garbage),
            'tracemalloc_snapshot': tracemalloc_snapshot
        }
        
        self.memory_snapshots.append(snapshot)
        return snapshot
    
    def analyze_object_growth(self, before_snapshot: Dict, after_snapshot: Dict) -> Dict[str, Any]:
        """Analyze object growth between snapshots."""
        before_counts = before_snapshot['object_counts']
        after_counts = after_snapshot['object_counts']
        
        growth_analysis = {
            'total_object_change': after_snapshot['total_objects'] - before_snapshot['total_objects'],
            'memory_change_mb': (after_snapshot['memory_rss'] - before_snapshot['memory_rss']) / 1024 / 1024,
            'object_type_changes': {},
            'new_object_types': [],
            'growing_object_types': [],
            'shrinking_object_types': []
        }
        
        # Analyze per-type changes
        all_types = set(before_counts.keys()) | set(after_counts.keys())
        
        for obj_type in all_types:
            before_count = before_counts.get(obj_type, 0)
            after_count = after_counts.get(obj_type, 0)
            change = after_count - before_count
            
            growth_analysis['object_type_changes'][obj_type] = {
                'before': before_count,
                'after': after_count,
                'change': change,
                'change_percent': (change / before_count * 100) if before_count > 0 else 0
            }
            
            if before_count == 0 and after_count > 0:
                growth_analysis['new_object_types'].append(obj_type)
            elif change > 0:
                growth_analysis['growing_object_types'].append((obj_type, change))
            elif change < 0:
                growth_analysis['shrinking_object_types'].append((obj_type, change))
        
        # Sort growing types by change amount
        growth_analysis['growing_object_types'].sort(key=lambda x: x[1], reverse=True)
        growth_analysis['shrinking_object_types'].sort(key=lambda x: x[1])
        
        return growth_analysis
    
    def run_sustained_operation_analysis(self, operations_count: int = 20) -> Dict[str, Any]:
        """
        Run sustained operation analysis to identify memory leak patterns.
        
        This simulates the conditions that caused the 10.08 MB/min leak.
        """
        print(f"Starting sustained operation analysis with {operations_count} operations...")
        
        # Create test dataset
        test_dir = self.create_test_dataset("medium")
        
        try:
            # Start memory tracking
            tracemalloc.start()
            
            # Take baseline snapshot
            baseline_snapshot = self.take_memory_snapshot("baseline")
            print(f"Baseline memory: {baseline_snapshot['memory_rss'] / 1024 / 1024:.2f} MB")
            
            # Create analyzer instance
            analyzer = SizeAnalyzer()
            
            # Run sustained operations
            operation_results = []
            
            for i in range(operations_count):
                print(f"Operation {i+1}/{operations_count}")
                
                # Take pre-operation snapshot
                pre_snapshot = self.take_memory_snapshot(f"pre_op_{i+1}")
                
                # Run analysis
                start_time = time.time()
                try:
                    result = analyzer.analyze_directory(test_dir)
                    success = True
                    error = None
                except Exception as e:
                    success = False
                    error = str(e)
                    result = None
                
                end_time = time.time()
                
                # Take post-operation snapshot
                post_snapshot = self.take_memory_snapshot(f"post_op_{i+1}")
                
                # Analyze growth for this operation
                growth_analysis = self.analyze_object_growth(pre_snapshot, post_snapshot)
                
                operation_result = {
                    'operation_id': i + 1,
                    'success': success,
                    'error': error,
                    'duration': end_time - start_time,
                    'files_analyzed': result.get('file_count', 0) if result else 0,
                    'memory_change_mb': growth_analysis['memory_change_mb'],
                    'object_count_change': growth_analysis['total_object_change'],
                    'top_growing_objects': growth_analysis['growing_object_types'][:5]
                }
                
                operation_results.append(operation_result)
                
                # Track cumulative memory growth
                cumulative_memory_mb = (post_snapshot['memory_rss'] - baseline_snapshot['memory_rss']) / 1024 / 1024
                print(f"  Memory change: +{growth_analysis['memory_change_mb']:.3f} MB "
                      f"(cumulative: +{cumulative_memory_mb:.3f} MB)")
                
                # Small delay between operations
                time.sleep(0.05)
            
            # Take final snapshot
            final_snapshot = self.take_memory_snapshot("final")
            
            # Analyze overall growth
            overall_growth = self.analyze_object_growth(baseline_snapshot, final_snapshot)
            
            # Calculate leak rate
            total_duration_minutes = (final_snapshot['timestamp'] - baseline_snapshot['timestamp']) / 60
            leak_rate_mb_per_min = overall_growth['memory_change_mb'] / total_duration_minutes if total_duration_minutes > 0 else 0
            
            analysis_results = {
                'test_configuration': {
                    'operations_count': operations_count,
                    'test_dataset_path': test_dir,
                    'total_duration_minutes': total_duration_minutes
                },
                'memory_leak_analysis': {
                    'total_memory_increase_mb': overall_growth['memory_change_mb'],
                    'leak_rate_mb_per_min': leak_rate_mb_per_min,
                    'leak_detected': leak_rate_mb_per_min > 1.0,  # >1 MB/min is significant
                    'total_object_increase': overall_growth['total_object_change']
                },
                'operation_results': operation_results,
                'object_growth_analysis': overall_growth,
                'memory_snapshots': self.memory_snapshots,
                'root_cause_diagnosis': self._diagnose_root_cause(overall_growth, operation_results)
            }
            
            return analysis_results
            
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(test_dir, ignore_errors=True)
            if tracemalloc.is_tracing():
                tracemalloc.stop()
    
    def _diagnose_root_cause(self, overall_growth: Dict, operation_results: List[Dict]) -> Dict[str, Any]:
        """Diagnose the root cause of memory leaks."""
        diagnosis = {
            'primary_leak_source': 'unknown',
            'leak_mechanism': 'unknown',
            'confidence_level': 0.0,
            'evidence': [],
            'specific_objects_leaking': [],
            'recommended_fixes': []
        }
        
        # Analyze top growing object types
        growing_objects = overall_growth.get('growing_object_types', [])
        
        if growing_objects:
            # Find the most significant growing object type
            top_growing = growing_objects[0]  # (type_name, change_count)
            obj_type, growth_count = top_growing
            
            diagnosis['primary_leak_source'] = obj_type
            diagnosis['confidence_level'] = min(0.9, growth_count / 100)  # Higher confidence for more objects
            diagnosis['evidence'].append(f"Object type '{obj_type}' increased by {growth_count} instances")
            
            # Analyze leak mechanism based on object type
            if obj_type in ['dict', 'defaultdict']:
                diagnosis['leak_mechanism'] = 'dictionary_accumulation'
                diagnosis['recommended_fixes'].extend([
                    "Clear dictionaries after each operation",
                    "Use weak references for caches",
                    "Implement cache size limits"
                ])
            elif obj_type in ['list', 'deque']:
                diagnosis['leak_mechanism'] = 'list_accumulation'
                diagnosis['recommended_fixes'].extend([
                    "Clear lists after each operation",
                    "Use generators instead of lists where possible",
                    "Implement list size monitoring"
                ])
            elif 'SizeAnalyzer' in obj_type:
                diagnosis['leak_mechanism'] = 'analyzer_instance_retention'
                diagnosis['recommended_fixes'].extend([
                    "Ensure SizeAnalyzer instances are properly garbage collected",
                    "Clear internal state after each operation",
                    "Use context managers for analyzer lifecycle"
                ])
            elif obj_type in ['str', 'unicode']:
                diagnosis['leak_mechanism'] = 'string_accumulation'
                diagnosis['recommended_fixes'].extend([
                    "Clear string caches and buffers",
                    "Use string interning carefully",
                    "Monitor progress message accumulation"
                ])
            else:
                diagnosis['leak_mechanism'] = 'object_reference_retention'
                diagnosis['recommended_fixes'].extend([
                    f"Investigate {obj_type} object lifecycle",
                    "Check for circular references",
                    "Implement explicit cleanup methods"
                ])
        
        # Analyze consistency across operations
        memory_changes = [op.get('memory_change_mb', 0) for op in operation_results if op.get('success', False)]
        if memory_changes:
            avg_change = sum(memory_changes) / len(memory_changes)
            if avg_change > 0.1:  # >0.1 MB per operation
                diagnosis['evidence'].append(f"Consistent memory growth: avg {avg_change:.3f} MB per operation")
                diagnosis['confidence_level'] = max(diagnosis['confidence_level'], 0.7)
        
        # Check for specific SizeAnalyzer patterns
        for op in operation_results:
            top_growing = op.get('top_growing_objects', [])
            for obj_type, count in top_growing:
                if 'SizeAnalyzer' in obj_type or 'progress' in obj_type.lower():
                    diagnosis['specific_objects_leaking'].append(obj_type)
                    diagnosis['evidence'].append(f"SizeAnalyzer-related object growth: {obj_type} (+{count})")
        
        return diagnosis
    
    def generate_comprehensive_report(self, analysis_results: Dict) -> str:
        """Generate a comprehensive root cause analysis report."""
        report_lines = [
            "=" * 80,
            "SIZEANALYZER MEMORY LEAK ROOT CAUSE ANALYSIS REPORT",
            "=" * 80,
            "",
            "EXECUTIVE SUMMARY:",
            f"- Total Memory Increase: {analysis_results['memory_leak_analysis']['total_memory_increase_mb']:.3f} MB",
            f"- Leak Rate: {analysis_results['memory_leak_analysis']['leak_rate_mb_per_min']:.3f} MB/min",
            f"- Leak Detected: {'YES' if analysis_results['memory_leak_analysis']['leak_detected'] else 'NO'}",
            f"- Operations Analyzed: {analysis_results['test_configuration']['operations_count']}",
            "",
            "ROOT CAUSE DIAGNOSIS:",
        ]
        
        diagnosis = analysis_results['root_cause_diagnosis']
        report_lines.extend([
            f"- Primary Leak Source: {diagnosis['primary_leak_source']}",
            f"- Leak Mechanism: {diagnosis['leak_mechanism']}",
            f"- Confidence Level: {diagnosis['confidence_level']:.1%}",
            ""
        ])
        
        if diagnosis['evidence']:
            report_lines.append("EVIDENCE:")
            for evidence in diagnosis['evidence']:
                report_lines.append(f"- {evidence}")
            report_lines.append("")
        
        if diagnosis['specific_objects_leaking']:
            report_lines.append("SPECIFIC LEAKING OBJECTS:")
            for obj in diagnosis['specific_objects_leaking']:
                report_lines.append(f"- {obj}")
            report_lines.append("")
        
        report_lines.append("TOP GROWING OBJECT TYPES:")
        growing_objects = analysis_results['object_growth_analysis']['growing_object_types'][:10]
        for obj_type, count in growing_objects:
            report_lines.append(f"- {obj_type}: +{count} instances")
        
        report_lines.extend([
            "",
            "RECOMMENDED FIXES:",
        ])
        
        for fix in diagnosis['recommended_fixes']:
            report_lines.append(f"- {fix}")
        
        report_lines.extend([
            "",
            "DETAILED OPERATION ANALYSIS:",
        ])
        
        successful_ops = [op for op in analysis_results['operation_results'] if op['success']]
        if successful_ops:
            avg_memory_change = sum(op['memory_change_mb'] for op in successful_ops) / len(successful_ops)
            max_memory_change = max(op['memory_change_mb'] for op in successful_ops)
            
            report_lines.extend([
                f"- Successful Operations: {len(successful_ops)}",
                f"- Average Memory Change: {avg_memory_change:.3f} MB per operation",
                f"- Maximum Memory Change: {max_memory_change:.3f} MB per operation",
            ])
        
        report_lines.extend([
            "",
            "=" * 80,
            "END OF ROOT CAUSE ANALYSIS REPORT",
            "=" * 80
        ])
        
        return "\n".join(report_lines)


def main():
    """Main execution function for root cause analysis."""
    print("Phase 2B-DEBUG: SizeAnalyzer Memory Leak Root Cause Analysis")
    print("=" * 60)
    
    analyzer = SizeAnalyzerMemoryLeakRootCauseAnalyzer()
    
    # Run comprehensive analysis
    results = analyzer.run_sustained_operation_analysis(operations_count=15)
    
    # Generate report
    report = analyzer.generate_comprehensive_report(results)
    print("\n" + report)
    
    # Save detailed results
    results_file = os.path.join(os.path.dirname(__file__), "sizeanalyzer_root_cause_analysis_2025-09-09.json")
    
    # Convert results to JSON-serializable format
    json_results = results.copy()
    # Remove non-serializable objects
    for snapshot in json_results.get('memory_snapshots', []):
        if 'tracemalloc_snapshot' in snapshot:
            snapshot['tracemalloc_snapshot'] = str(snapshot['tracemalloc_snapshot'])
    
    with open(results_file, 'w') as f:
        json.dump(json_results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    # Summary for quick assessment
    leak_detected = results['memory_leak_analysis']['leak_detected']
    leak_rate = results['memory_leak_analysis']['leak_rate_mb_per_min']
    primary_source = results['root_cause_diagnosis']['primary_leak_source']
    
    print("\n" + "=" * 60)
    print("QUICK ASSESSMENT:")
    print(f"Memory Leak Detected: {'YES' if leak_detected else 'NO'}")
    print(f"Leak Rate: {leak_rate:.3f} MB/min")
    print(f"Primary Source: {primary_source}")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    main()