#!/usr/bin/env python3
"""
Corrected Comprehensive Test Script for Multi-Pane Explorer Compatibility Matrix
Tests 12 combinations of 4 pane variants and 3 layout variants (corrected from test)

This test systematically validates:
- 4 Pane Variants: 1-pane, 2-pane, 3-pane, 4-pane
- 3 Layout Variants: Horizontal, Vertical, Grid (mixed mode does not exist)

Author: Principal Engineer - Enterprise Technical Analysis
Created: 2025-01-13 (Corrected Version)
Purpose: Identify and document compatibility issues in multi-pane explorer system
"""

import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication, QWidget
except ImportError as e:
    print(f"PyQt5 import error: {e}")
    sys.exit(1)

try:
    from src.config_manager import get_config_manager
    from src.file_explorer.multi_pane_explorer import MultiPaneFileExplorer
except ImportError as e:
    print(f"RFU import error: {e}")
    sys.exit(1)


class CorrectedPaneLayoutCompatibilityTester:
    """
    Comprehensive test framework for pane-layout compatibility matrix analysis
    
    Tests 12 combinations of:
    - Pane configurations: 1, 2, 3, 4 panes
    - Layout configurations: Horizontal, Vertical, Grid (corrected from initial test)
    """
    
    def __init__(self):
        self.app = None
        self.explorer = None
        self.test_results = {}
        self.config_manager = get_config_manager()
        self.test_start_time = datetime.now()
        
        # Define CORRECTED test matrix based on actual implementation
        self.pane_variants = [1, 2, 3, 4]
        self.layout_variants = ['Horizontal', 'Vertical', 'Grid']  # Corrected: no 'mixed'
        
        # Test results tracking
        self.successful_combinations = []
        self.failed_combinations = []
        self.blank_combinations = []
        self.error_combinations = []
        
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
            
            # Show the explorer to ensure proper initialization
            self.explorer.show()
            
            # Wait for full initialization
            self.app.processEvents()
            time.sleep(1.0)  # Longer wait for proper initialization
            
            print("✅ Test environment setup successful")
            print(f"   Explorer visible: {self.explorer.isVisible()}")
            print(f"   Has layout_combo: {hasattr(self.explorer, 'layout_combo')}")
            
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
            layout_mode: Layout mode ('Horizontal', 'Vertical', 'Grid')
            
        Returns:
            Dictionary with test results and analysis
        """
        test_id = f"{pane_count}pane_{layout_mode.lower()}"
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
            time.sleep(0.3)
            
            # Step 2: Set layout mode using CORRECTED attribute name
            print(f"   Setting layout mode to {layout_mode}...")
            
            # Check if layout_combo exists (corrected from layout_mode_combo)
            if hasattr(self.explorer, 'layout_combo'):
                combo = self.explorer.layout_combo
                layout_index = -1
                
                # Find exact layout mode in combo box
                for i in range(combo.count()):
                    if combo.itemText(i) == layout_mode:  # Exact match
                        layout_index = i
                        break
                        
                if layout_index >= 0:
                    print(f"   Found layout '{layout_mode}' at index {layout_index}")
                    combo.setCurrentIndex(layout_index)
                    self.app.processEvents()
                    time.sleep(0.3)
                else:
                    available_layouts = [combo.itemText(i) for i in range(combo.count())]
                    result['error'] = f"Layout mode '{layout_mode}' not found. Available: {available_layouts}"
                    print(f"   ⚠️  Layout mode not found. Available: {available_layouts}")
                    return result
            else:
                result['error'] = "Layout combo box not found in explorer instance"
                print(f"   ⚠️  Layout combo not found")
                return result
                
            # Step 3: Force layout update
            if hasattr(self.explorer, '_update_pane_layout'):
                print("   Updating pane layout...")
                self.explorer._update_pane_layout()
                self.app.processEvents()
                time.sleep(0.5)
            
            # Step 4: Analyze resulting layout
            result.update(self._analyze_layout_state())
            
            # Step 5: Check for content
            content_check = self._check_pane_content()
            result.update(content_check)
            
            # Step 6: Determine success status
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
            'layout_geometry': None,
            'splitter_info': None
        }
        
        try:
            # Count main widgets
            if hasattr(self.explorer, 'central_widget'):
                central = self.explorer.central_widget
                if central:
                    all_widgets = central.findChildren(QWidget)
                    analysis['widget_count'] = len(all_widgets)
                    analysis['visible_widgets'] = len([w for w in all_widgets if w.isVisible()])
                    
            # Analyze pane widgets specifically
            if hasattr(self.explorer, 'panes'):
                panes = self.explorer.panes
                for i, pane in enumerate(panes):
                    pane_info = {
                        'index': i,
                        'exists': pane is not None,
                        'visible': pane.isVisible() if pane else False,
                        'size': pane.size().width() * pane.size().height() if pane and pane.isVisible() else 0,
                        'has_children': len(pane.findChildren(QWidget)) > 0 if pane else False,
                        'child_count': len(pane.findChildren(QWidget)) if pane else 0
                    }
                    analysis['pane_widgets'].append(pane_info)
                    
            # Analyze splitter state
            if hasattr(self.explorer, 'pane_splitter'):
                splitter = self.explorer.pane_splitter
                if splitter:
                    analysis['splitter_info'] = {
                        'orientation': 'Horizontal' if splitter.orientation() == Qt.Horizontal else 'Vertical',
                        'count': splitter.count(),
                        'visible': splitter.isVisible(),
                        'sizes': splitter.sizes()
                    }
                    
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
            'content_panes': 0,
            'total_panes_checked': 0
        }
        
        try:
            if hasattr(self.explorer, 'panes'):
                panes = self.explorer.panes
                content_check['total_panes_checked'] = len(panes)
                
                for i, pane in enumerate(panes):
                    if not pane:
                        content_check['empty_panes'] += 1
                        content_check['content_summary'][f'pane_{i}'] = {
                            'exists': False,
                            'reason': 'Pane is None'
                        }
                        continue
                        
                    if not pane.isVisible():
                        content_check['empty_panes'] += 1
                        content_check['content_summary'][f'pane_{i}'] = {
                            'exists': True,
                            'visible': False,
                            'reason': 'Pane not visible'
                        }
                        continue
                        
                    # Check for meaningful widgets in pane
                    child_widgets = pane.findChildren(QWidget)
                    meaningful_widgets = []
                    
                    for widget in child_widgets:
                        widget_type = type(widget).__name__
                        # Look for file browser related widgets
                        if any(content_type in widget_type.lower() for content_type in 
                               ['tree', 'list', 'table', 'view', 'browser', 'explorer', 'model']):
                            meaningful_widgets.append(widget_type)
                            
                    has_meaningful_content = len(meaningful_widgets) > 0
                    
                    if has_meaningful_content:
                        content_check['content_panes'] += 1
                    else:
                        content_check['empty_panes'] += 1
                        
                    content_check['content_summary'][f'pane_{i}'] = {
                        'exists': True,
                        'visible': True,
                        'has_content': has_meaningful_content,
                        'widget_count': len(child_widgets),
                        'meaningful_widgets': meaningful_widgets[:3],  # First 3 types
                        'all_widget_types': [type(w).__name__ for w in child_widgets[:5]]
                    }
                    
            content_check['has_content'] = content_check['content_panes'] > 0
            
        except Exception as e:
            content_check['content_check_error'] = str(e)
            
        return content_check
        
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run complete compatibility matrix test"""
        print("🚀 Starting CORRECTED Comprehensive Pane-Layout Compatibility Test")
        print("=" * 80)
        
        if not self.setup_test_environment():
            return {'error': 'Failed to setup test environment'}
            
        # Test all combinations (12 total: 4 panes × 3 layouts)
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
                test_id = f"{pane_count}pane_{layout_mode.lower()}"
                
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
                    
                matrix[f'{pane_count}_pane'][layout_mode.lower()] = status
                
        return matrix
        
    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate technical recommendations based on test results"""
        recommendations = []
        
        # Analyze patterns in failures
        if self.blank_combinations:
            recommendations.append({
                'issue': 'Blank Content Combinations',
                'combinations': ', '.join(self.blank_combinations),
                'recommendation': 'Investigate widget initialization and content loading in _add_panes() method. Check FileExplorerPane creation and set_path functionality.',
                'priority': 'HIGH'
            })
            
        if self.error_combinations:
            recommendations.append({
                'issue': 'Error-Prone Combinations',
                'combinations': ', '.join(self.error_combinations),
                'recommendation': 'Review exception handling in layout switching and pane creation. Add validation for combo box state.',
                'priority': 'CRITICAL'
            })
            
        # Check for specific pattern issues
        grid_issues = [combo for combo in (self.blank_combinations + self.error_combinations + self.failed_combinations) if 'grid' in combo]
        if grid_issues:
            recommendations.append({
                'issue': 'Grid Layout Issues',
                'combinations': ', '.join(grid_issues),
                'recommendation': 'Debug _create_grid_layout() method and 2x2 grid widget placement for 4-pane scenarios',
                'priority': 'HIGH'
            })
            
        four_pane_issues = [combo for combo in (self.blank_combinations + self.error_combinations + self.failed_combinations) if '4pane' in combo]
        if four_pane_issues:
            recommendations.append({
                'issue': '4-Pane Configuration Issues',
                'combinations': ', '.join(four_pane_issues),
                'recommendation': 'Verify 4-pane layout logic in _update_pane_layout() and ensure proper splitter configuration',
                'priority': 'HIGH'
            })
            
        return recommendations
        
    def _save_test_results(self, analysis: Dict[str, Any]) -> None:
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"corrected_pane_layout_compatibility_test_{timestamp}.json"
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
        print("📊 CORRECTED PANE-LAYOUT COMPATIBILITY TEST SUMMARY")
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
            print(f"{layout.lower():<12}", end="")
        print()
        
        # Print matrix rows
        for pane_config, layouts in matrix.items():
            print(f"{pane_config:<10}", end="")
            for layout in self.layout_variants:
                status = layouts.get(layout.lower(), "❓ UNKNOWN")
                print(f"{status:<12}", end="")
            print()
            
        if analysis['recommendations']:
            print("\n💡 TECHNICAL RECOMMENDATIONS:")
            for i, rec in enumerate(analysis['recommendations'], 1):
                print(f"{i}. [{rec['priority']}] {rec['issue']}")
                print(f"   🔧 {rec['recommendation']}")
                print(f"   📍 Affects: {rec['combinations']}")
                print()


def main():
    """Main execution function"""
    print("🏗️  Principal Engineer Technical Analysis: Multi-Pane Explorer Compatibility Matrix")
    print("🔬 Testing 12 combinations of pane variants (1-4) and layout variants (3)")
    print("🎯 Identifying blank/empty result combinations for systematic remediation")
    
    tester = CorrectedPaneLayoutCompatibilityTester()
    
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