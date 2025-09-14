#!/usr/bin/env python3
"""
Comprehensive Test Script for Multi-Pane Explorer Pane-Layout Compatibility Matrix
Tests all 16 combinations of 4 pane variants and 4 layout variants to identify blank/empty results

This test systematically validates:
- 4 Pane Variants: 1-pane, 2-pane, 3-pane, 4-pane
- 4 Layout Variants: horizontal, vertical, grid, mixed (if available)

Author: Principal Engineer - Enterprise Technical Analysis
Created: 2025-01-13
Purpose: Identify and document compatibility issues in the multi-pane explorer system
"""

import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from PyQt5.QtCore import QObject, QTimer, pyqtSignal
    from PyQt5.QtTest import QTest
    from PyQt5.QtWidgets import (QApplication, QLabel, QMainWindow,
                                 QVBoxLayout, QWidget)
except ImportError as e:
    print(f"PyQt5 import error: {e}")
    sys.exit(1)

try:
    from src.rfu.config_manager import get_config_manager
    from src.rfu.file_explorer.multi_pane_explorer import MultiPaneFileExplorer
except ImportError as e:
    print(f"RFU import error: {e}")
    sys.exit(1)

class PaneLayoutCompatibilityTester:
    """
    Comprehensive test framework for pane-layout compatibility matrix analysis
    
    Tests all 16 combinations of:
    - Pane configurations: 1, 2, 3, 4 panes
    - Layout configurations: horizontal, vertical, grid, mixed
    """
    
    def __init__(self):
        self.app = None
        self.explorer = None
        self.test_results = {}
        self.config_manager = get_config_manager()
        self.test_start_time = datetime.now()
        
        # Define test matrix
        self.pane_variants = [1, 2, 3, 4]
        self.layout_variants = ['horizontal', 'vertical', 'grid', 'mixed']
        
        # Test results tracking
        self.successful_combinations = []
        self.failed_combinations = []
        self.blank_combinations = []
        self.error_combinations = []
        
        # Detailed error tracking
        self.detailed_errors = {}
        
    def setup_test_environment(self) -> bool:
        """Initialize PyQt5 application and multi-pane explorer for testing"""
        try:
            # Create QApplication if not exists
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
            else:
                self.app = QApplication.instance()
                
            # Initialize multi-pane explorer
            self.explorer = MultiPaneFileExplorer()
            
            # Wait for initialization
            self.app.processEvents()
            time.sleep(0.5)
            
            print("✅ Test environment setup successful")
            return True
            
        except Exception as e:
            print(f"❌ Test environment setup failed: {e}")
            traceback.print_exc()
            return False
            
    def test_pane_layout_combination(self, pane_count: int, layout_mode: str) -> Dict[str, Any]:
        """
        Test a specific pane-layout combination
        
        Args:
            pane_count: Number of panes (1-4)
            layout_mode: Layout mode ('horizontal', 'vertical', 'grid', 'mixed')
            
        Returns:
            Dictionary with test results and analysis
        """
        test_id = f"{pane_count}pane_{layout_mode}"
        print(f"\n🔬 Testing combination: {test_id}")
        
        result = {
            'test_id': test_id,
            'pane_count': pane_count,
            'layout_mode': layout_mode,
            'success': False,
            'has_content': False,
            'error': None,
            'error_traceback': None,
            'widget_count': 0,
            'visible_widgets': 0,
            'pane_widgets': [],
            'layout_geometry': None,
            'test_timestamp': datetime.now().isoformat()
        }
        
        try:
            # Step 1: Set pane count
            print(f"   Setting pane count to {pane_count}...")
            self.explorer.set_pane_count(pane_count)
            self.app.processEvents()
            time.sleep(0.2)
            
            # Step 2: Set layout mode
            print(f"   Setting layout mode to {layout_mode}...")
            
            # Check if layout mode is available
            if hasattr(self.explorer, 'layout_mode_combo'):
                combo = self.explorer.layout_mode_combo
                layout_index = -1
                
                # Find layout mode in combo box
                for i in range(combo.count()):
                    if layout_mode.lower() in combo.itemText(i).lower():
                        layout_index = i
                        break
                        
                if layout_index >= 0:
                    combo.setCurrentIndex(layout_index)
                    self.app.processEvents()
                    time.sleep(0.2)
                else:
                    result['error'] = f"Layout mode '{layout_mode}' not found in combo box"
                    print(f"   ⚠️  Layout mode not found")
                    return result
            else:
                result['error'] = "Layout mode combo box not found"
                print(f"   ⚠️  Layout combo not found")
                return result
                
            # Step 3: Force layout update
            if hasattr(self.explorer, '_update_pane_layout'):
                self.explorer._update_pane_layout()
                self.app.processEvents()
                time.sleep(0.3)
            
            # Step 4: Analyze resulting layout
            result.update(self._analyze_layout_state())
            
            # Step 5: Check for content
            content_check = self._check_pane_content()
            result.update(content_check)
            
            if result['widget_count'] > 0 and result['has_content']:
                result['success'] = True
                print(f"   ✅ Success: {result['widget_count']} widgets, content present")
                self.successful_combinations.append(test_id)
            elif result['widget_count'] > 0 and not result['has_content']:
                result['success'] = False
                print(f"   ⚠️  Blank: {result['widget_count']} widgets, no content")
                self.blank_combinations.append(test_id)
            else:
                result['success'] = False
                print(f"   ❌ Failed: No widgets created")
                self.failed_combinations.append(test_id)
                
        except Exception as e:
            result['error'] = str(e)
            result['error_traceback'] = traceback.format_exc()
            print(f"   💥 Error: {e}")
            self.error_combinations.append(test_id)
            
        return result
        
    def _analyze_layout_state(self) -> Dict[str, Any]:
        """Analyze the current layout state of the explorer"""
        analysis = {
            'widget_count': 0,
            'visible_widgets': 0,
            'pane_widgets': [],
            'layout_geometry': None
        }
        
        try:
            # Count main widgets
            if hasattr(self.explorer, 'central_widget'):
                central = self.explorer.central_widget
                if central:
                    analysis['widget_count'] = len(central.findChildren(QWidget))
                    analysis['visible_widgets'] = len([w for w in central.findChildren(QWidget) if w.isVisible()])
                    
            # Analyze pane widgets specifically
            if hasattr(self.explorer, 'panes'):
                panes = self.explorer.panes
                for i, pane in enumerate(panes):
                    pane_info = {
                        'index': i,
                        'visible': pane.isVisible() if pane else False,
                        'size': pane.size().width() * pane.size().height() if pane and pane.isVisible() else 0,
                        'has_children': len(pane.findChildren(QWidget)) > 0 if pane else False
                    }
                    analysis['pane_widgets'].append(pane_info)
                    
            # Get layout geometry
            if hasattr(self.explorer, 'geometry'):
                geo = self.explorer.geometry()
                analysis['layout_geometry'] = {
                    'width': geo.width(),
                    'height': geo.height(),
                    'x': geo.x(),
                    'y': geo.y()
                }
                
        except Exception as e:
            analysis['analysis_error'] = str(e)
            
        return analysis
        
    def _check_pane_content(self) -> Dict[str, Any]:
        """Check if panes actually contain meaningful content"""
        content_check = {
            'has_content': False,
            'content_summary': {},
            'empty_panes': 0,
            'content_panes': 0
        }
        
        try:
            if hasattr(self.explorer, 'panes'):
                panes = self.explorer.panes
                
                for i, pane in enumerate(panes):
                    if not pane or not pane.isVisible():
                        content_check['empty_panes'] += 1
                        continue
                        
                    # Check for file browser content
                    file_browsers = pane.findChildren(QWidget)
                    has_meaningful_content = False
                    
                    for widget in file_browsers:
                        # Check for tree views, list views, tables, etc.
                        widget_type = type(widget).__name__
                        if any(content_type in widget_type.lower() for content_type in 
                               ['tree', 'list', 'table', 'view', 'browser', 'explorer']):
                            has_meaningful_content = True
                            break
                            
                    if has_meaningful_content:
                        content_check['content_panes'] += 1
                    else:
                        content_check['empty_panes'] += 1
                        
                    content_check['content_summary'][f'pane_{i}'] = {
                        'has_content': has_meaningful_content,
                        'widget_count': len(file_browsers),
                        'widget_types': [type(w).__name__ for w in file_browsers[:5]]  # First 5 types
                    }
                    
            content_check['has_content'] = content_check['content_panes'] > 0
            
        except Exception as e:
            content_check['content_check_error'] = str(e)
            
        return content_check
        
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run complete compatibility matrix test"""
        print("🚀 Starting Comprehensive Pane-Layout Compatibility Test")
        print("=" * 80)
        
        if not self.setup_test_environment():
            return {'error': 'Failed to setup test environment'}
            
        # Test all combinations
        for pane_count in self.pane_variants:
            for layout_mode in self.layout_variants:
                test_result = self.test_pane_layout_combination(pane_count, layout_mode)
                self.test_results[test_result['test_id']] = test_result
                
        # Generate comprehensive analysis
        analysis = self._generate_analysis_report()
        
        # Save results
        self._save_test_results(analysis)
        
        print("\n" + "=" * 80)
        print("🏁 Comprehensive Test Complete")
        
        return analysis
        
    def _generate_analysis_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis of test results"""
        report = {
            'test_metadata': {
                'test_start_time': self.test_start_time.isoformat(),
                'test_end_time': datetime.now().isoformat(),
                'total_combinations_tested': len(self.test_results),
                'test_matrix': {
                    'pane_variants': self.pane_variants,
                    'layout_variants': self.layout_variants
                }
            },
            'summary_statistics': {
                'successful_combinations': len(self.successful_combinations),
                'failed_combinations': len(self.failed_combinations),
                'blank_combinations': len(self.blank_combinations),
                'error_combinations': len(self.error_combinations),
                'success_rate': len(self.successful_combinations) / len(self.test_results) * 100 if self.test_results else 0
            },
            'detailed_results': self.test_results,
            'problem_combinations': {
                'blank_results': self.blank_combinations,
                'errors': self.error_combinations,
                'failures': self.failed_combinations
            },
            'compatibility_matrix': self._build_compatibility_matrix(),
            'recommendations': self._generate_recommendations()
        }
        
        return report
        
    def _build_compatibility_matrix(self) -> Dict[str, Dict[str, str]]:
        """Build visual compatibility matrix"""
        matrix = {}
        
        for pane_count in self.pane_variants:
            matrix[f'{pane_count}_pane'] = {}
            for layout_mode in self.layout_variants:
                test_id = f"{pane_count}pane_{layout_mode}"
                
                if test_id in self.successful_combinations:
                    status = "✅ SUCCESS"
                elif test_id in self.blank_combinations:
                    status = "⚠️  BLANK"
                elif test_id in self.error_combinations:
                    status = "💥 ERROR"
                elif test_id in self.failed_combinations:
                    status = "❌ FAILED"
                else:
                    status = "❓ UNKNOWN"
                    
                matrix[f'{pane_count}_pane'][layout_mode] = status
                
        return matrix
        
    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate technical recommendations based on test results"""
        recommendations = []
        
        # Analyze patterns in failures
        if self.blank_combinations:
            recommendations.append({
                'issue': 'Blank Content Combinations',
                'combinations': ', '.join(self.blank_combinations),
                'recommendation': 'Check widget initialization and content loading in _add_panes() and _update_pane_layout() methods',
                'priority': 'HIGH'
            })
            
        if self.error_combinations:
            recommendations.append({
                'issue': 'Error-Prone Combinations',
                'combinations': ', '.join(self.error_combinations),
                'recommendation': 'Review exception handling and validate layout mode availability before setting',
                'priority': 'CRITICAL'
            })
            
        # Check for specific pattern issues
        pane_4_issues = [combo for combo in (self.blank_combinations + self.error_combinations + self.failed_combinations) if '4pane_' in combo]
        if pane_4_issues:
            recommendations.append({
                'issue': '4-Pane Configuration Issues',
                'combinations': ', '.join(pane_4_issues),
                'recommendation': 'Verify grid layout implementation in _create_grid_layout() for 4-pane scenarios',
                'priority': 'HIGH'
            })
            
        grid_issues = [combo for combo in (self.blank_combinations + self.error_combinations + self.failed_combinations) if '_grid' in combo]
        if grid_issues:
            recommendations.append({
                'issue': 'Grid Layout Issues',
                'combinations': ', '.join(grid_issues),
                'recommendation': 'Debug grid layout algorithm and widget placement logic',
                'priority': 'HIGH'
            })
            
        return recommendations
        
    def _save_test_results(self, analysis: Dict[str, Any]) -> None:
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pane_layout_compatibility_test_{timestamp}.json"
        filepath = Path(__file__).parent / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, default=str)
            print(f"📄 Test results saved to: {filepath}")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
            
    def print_summary_report(self, analysis: Dict[str, Any]) -> None:
        """Print formatted summary report to console"""
        print("\n" + "=" * 80)
        print("📊 PANE-LAYOUT COMPATIBILITY TEST SUMMARY")
        print("=" * 80)
        
        stats = analysis['summary_statistics']
        print(f"✅ Successful: {stats['successful_combinations']} combinations")
        print(f"⚠️  Blank Results: {stats['blank_combinations']} combinations")
        print(f"❌ Failed: {stats['failed_combinations']} combinations")
        print(f"💥 Errors: {stats['error_combinations']} combinations")
        print(f"📈 Success Rate: {stats['success_rate']:.1f}%")
        
        print("\n📋 COMPATIBILITY MATRIX:")
        matrix = analysis['compatibility_matrix']
        
        # Print header
        print(f"{'Panes':<10}", end="")
        for layout in self.layout_variants:
            print(f"{layout:<12}", end="")
        print()
        
        # Print matrix rows
        for pane_config, layouts in matrix.items():
            print(f"{pane_config:<10}", end="")
            for layout in self.layout_variants:
                status = layouts.get(layout, "❓ UNKNOWN")
                print(f"{status:<12}", end="")
            print()
            
        if analysis['recommendations']:
            print("\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(analysis['recommendations'], 1):
                print(f"{i}. [{rec['priority']}] {rec['issue']}")
                print(f"   🔧 {rec['recommendation']}")
                print(f"   📍 Affects: {rec['combinations']}")
                print()

def main():
    """Main execution function"""
    print("🏗️  Principal Engineer Technical Analysis: Multi-Pane Explorer Compatibility Matrix")
    print("🔬 Testing all 16 combinations of pane variants (1-4) and layout variants (4)")
    print("🎯 Identifying blank/empty result combinations for systematic remediation")
    
    tester = PaneLayoutCompatibilityTester()
    
    try:
        # Run comprehensive test
        analysis = tester.run_comprehensive_test()
        
        # Print summary
        tester.print_summary_report(analysis)
        
        # Return success
        return 0
        
    except Exception as e:
        print(f"💥 Critical test failure: {e}")
        traceback.print_exc()
        return 1
    finally:
        # Cleanup
        if tester.app:
            tester.app.quit()

if __name__ == "__main__":
    sys.exit(main())