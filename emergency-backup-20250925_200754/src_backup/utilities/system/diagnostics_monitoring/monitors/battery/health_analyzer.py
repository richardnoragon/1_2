"""Battery health analysis and degradation tracking."""

import logging
import json
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ...core.platform_detector import get_platform_detector
from core.error_handler import error_handler


class BatteryHealthStatus(Enum):
    """Battery health status levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class BatteryHealthMetrics:
    """Battery health metrics data structure."""
    capacity_health: float  # Percentage of original capacity
    cycle_count: int
    age_months: float
    temperature_avg: Optional[float]
    voltage_health: Optional[float]
    degradation_rate: float  # Capacity loss per month
    estimated_lifespan_months: Optional[float]
    health_status: BatteryHealthStatus
    recommendations: List[str]


class BatteryHealthAnalyzer:
    """Analyzes battery health and tracks degradation over time."""
    
    def __init__(self):
        """Initialize the battery health analyzer."""
        self.logger = logging.getLogger(
            'RFU.DiagnosticsMonitoring.BatteryHealthAnalyzer'
        )
        self.platform_detector = get_platform_detector()
        
        # Health tracking data
        self._health_history: Dict[str, List[Dict[str, Any]]] = {}
        self._baseline_data: Dict[str, Dict[str, Any]] = {}
        self._degradation_models: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self._config_dir = self.platform_detector.get_config_directory()
        self._health_data_file = os.path.join(
            self._config_dir, "battery_health_data.json"
        )
        
        # Health thresholds
        self.health_thresholds = {
            BatteryHealthStatus.EXCELLENT: 95.0,
            BatteryHealthStatus.GOOD: 85.0,
            BatteryHealthStatus.FAIR: 70.0,
            BatteryHealthStatus.POOR: 50.0,
            BatteryHealthStatus.CRITICAL: 30.0
        }
        
        # Load existing health data
        self._load_health_data()
        
        self.logger.info("Battery health analyzer initialized")
    
    def initialize(self, platform) -> None:
        """Initialize platform-specific health analysis.
        
        Args:
            platform: Target platform for initialization
        """
        try:
            # Create config directory if it doesn't exist
            os.makedirs(self._config_dir, exist_ok=True)
            
            # Initialize platform-specific health models
            self._initialize_degradation_models(platform)
            
            self.logger.info(f"Health analyzer initialized for {platform.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize health analyzer: {e}")
            error_handler.handle_error(e, "BatteryHealthAnalyzer.initialize")
    
    def _initialize_degradation_models(self, platform) -> None:
        """Initialize battery degradation models for the platform.
        
        Args:
            platform: Target platform
        """
        try:
            # Default degradation model parameters
            default_model = {
                'linear_degradation_rate': 0.2,  # % per month
                'cycle_degradation_factor': 0.01,  # % per 100 cycles
                'temperature_factor': 0.05,  # Additional degradation per °C above 25°C
                'age_acceleration_factor': 1.1,  # Exponential aging factor
                'expected_lifespan_cycles': 1000,
                'expected_lifespan_months': 36
            }
            
            # Platform-specific adjustments
            if platform.value == 'windows':
                # Windows laptops often have more aggressive power management
                default_model['linear_degradation_rate'] = 0.25
            elif platform.value == 'macos':
                # MacBooks generally have better battery management
                default_model['linear_degradation_rate'] = 0.15
                default_model['expected_lifespan_cycles'] = 1200
            elif platform.value == 'linux':
                # Linux systems vary widely, use conservative estimates
                default_model['linear_degradation_rate'] = 0.3
            
            self._degradation_models['default'] = default_model
            
        except Exception as e:
            self.logger.error(f"Error initializing degradation models: {e}")
    
    def analyze_battery_health(
        self, 
        battery_id: str, 
        battery_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze battery health and return comprehensive health metrics.
        
        Args:
            battery_id: Battery identifier
            battery_data: Current battery data
            
        Returns:
            Dict containing health analysis results
        """
        try:
            # Get or create baseline data
            if battery_id not in self._baseline_data:
                self._establish_baseline(battery_id, battery_data)
            
            # Calculate health metrics
            metrics = self._calculate_health_metrics(battery_id, battery_data)
            
            # Store health data point
            self._store_health_data_point(battery_id, battery_data, metrics)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(metrics, battery_data)
            
            # Prepare health analysis result
            health_analysis = {
                'health_percent': metrics.capacity_health,
                'health_status': metrics.health_status.value,
                'cycle_count': metrics.cycle_count,
                'age_months': metrics.age_months,
                'degradation_rate_per_month': metrics.degradation_rate,
                'estimated_lifespan_months': metrics.estimated_lifespan_months,
                'temperature_avg_c': metrics.temperature_avg,
                'voltage_health_percent': metrics.voltage_health,
                'recommendations': recommendations,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return health_analysis
            
        except Exception as e:
            self.logger.error(
                f"Error analyzing battery health for {battery_id}: {e}"
            )
            return {}
    
    def _establish_baseline(
        self, 
        battery_id: str, 
        battery_data: Dict[str, Any]
    ) -> None:
        """Establish baseline data for a new battery.
        
        Args:
            battery_id: Battery identifier
            battery_data: Initial battery data
        """
        try:
            baseline = {
                'established_date': datetime.now().isoformat(),
                'design_capacity_wh': battery_data.get('design_capacity_wh'),
                'design_capacity_mah': battery_data.get('design_capacity_mah'),
                'design_voltage': battery_data.get('design_voltage'),
                'initial_cycle_count': battery_data.get('cycle_count', 0),
                'manufacturer': battery_data.get('manufacturer'),
                'model': battery_data.get('model'),
                'serial_number': battery_data.get('serial_number'),
                'chemistry': battery_data.get('chemistry')
            }
            
            self._baseline_data[battery_id] = baseline
            self._save_health_data()
            
            self.logger.info(f"Established baseline for battery {battery_id}")
            
        except Exception as e:
            self.logger.error(f"Error establishing baseline for {battery_id}: {e}")
    
    def _calculate_health_metrics(
        self, 
        battery_id: str, 
        battery_data: Dict[str, Any]
    ) -> BatteryHealthMetrics:
        """Calculate comprehensive health metrics for a battery.
        
        Args:
            battery_id: Battery identifier
            battery_data: Current battery data
            
        Returns:
            BatteryHealthMetrics object with calculated metrics
        """
        try:
            baseline = self._baseline_data.get(battery_id, {})
            
            # Calculate capacity health
            capacity_health = self._calculate_capacity_health(
                battery_data, baseline
            )
            
            # Get cycle count
            cycle_count = battery_data.get('cycle_count', 0)
            
            # Calculate age
            age_months = self._calculate_battery_age(baseline)
            
            # Calculate average temperature
            temperature_avg = self._calculate_average_temperature(battery_id)
            
            # Calculate voltage health
            voltage_health = self._calculate_voltage_health(
                battery_data, baseline
            )
            
            # Calculate degradation rate
            degradation_rate = self._calculate_degradation_rate(
                battery_id, capacity_health, age_months
            )
            
            # Estimate remaining lifespan
            estimated_lifespan = self._estimate_remaining_lifespan(
                capacity_health, degradation_rate, cycle_count
            )
            
            # Determine health status
            health_status = self._determine_health_status(
                capacity_health, cycle_count, age_months
            )
            
            # Generate recommendations
            recommendations = self._generate_health_recommendations(
                capacity_health, cycle_count, temperature_avg, degradation_rate
            )
            
            return BatteryHealthMetrics(
                capacity_health=capacity_health,
                cycle_count=cycle_count,
                age_months=age_months,
                temperature_avg=temperature_avg,
                voltage_health=voltage_health,
                degradation_rate=degradation_rate,
                estimated_lifespan_months=estimated_lifespan,
                health_status=health_status,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating health metrics: {e}")
            return BatteryHealthMetrics(
                capacity_health=100.0,
                cycle_count=0,
                age_months=0.0,
                temperature_avg=None,
                voltage_health=None,
                degradation_rate=0.0,
                estimated_lifespan_months=None,
                health_status=BatteryHealthStatus.UNKNOWN,
                recommendations=[]
            )
    
    def _calculate_capacity_health(
        self, 
        battery_data: Dict[str, Any], 
        baseline: Dict[str, Any]
    ) -> float:
        """Calculate battery capacity health percentage.
        
        Args:
            battery_data: Current battery data
            baseline: Baseline battery data
            
        Returns:
            Capacity health as percentage of original capacity
        """
        try:
            current_capacity = battery_data.get('current_capacity_wh')
            design_capacity = baseline.get('design_capacity_wh')
            
            if current_capacity is None:
                current_capacity = battery_data.get('current_capacity_mah')
                design_capacity = baseline.get('design_capacity_mah')
            
            if current_capacity and design_capacity and design_capacity > 0:
                health_percent = (current_capacity / design_capacity) * 100.0
                return min(100.0, max(0.0, health_percent))
            
            # Fallback: estimate from charge percentage and voltage
            charge_percent = battery_data.get('percent', 100.0)
            current_voltage = battery_data.get('voltage')
            design_voltage = baseline.get('design_voltage')
            
            if current_voltage and design_voltage and design_voltage > 0:
                voltage_ratio = current_voltage / design_voltage
                estimated_health = charge_percent * voltage_ratio
                return min(100.0, max(0.0, estimated_health))
            
            # Last resort: assume 100% if no degradation data available
            return 100.0
            
        except Exception as e:
            self.logger.error(f"Error calculating capacity health: {e}")
            return 100.0
    
    def _calculate_battery_age(self, baseline: Dict[str, Any]) -> float:
        """Calculate battery age in months.
        
        Args:
            baseline: Baseline battery data
            
        Returns:
            Battery age in months
        """
        try:
            established_date_str = baseline.get('established_date')
            if not established_date_str:
                return 0.0
            
            established_date = datetime.fromisoformat(established_date_str)
            age_delta = datetime.now() - established_date
            age_months = age_delta.days / 30.44  # Average days per month
            
            return max(0.0, age_months)
            
        except Exception as e:
            self.logger.error(f"Error calculating battery age: {e}")
            return 0.0
    
    def _calculate_average_temperature(self, battery_id: str) -> Optional[float]:
        """Calculate average temperature from recent history.
        
        Args:
            battery_id: Battery identifier
            
        Returns:
            Average temperature in Celsius or None if not available
        """
        try:
            history = self._health_history.get(battery_id, [])
            if not history:
                return None
            
            # Get temperatures from last 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            recent_temps = []
            
            for entry in history:
                entry_date = datetime.fromisoformat(entry['timestamp'])
                if entry_date > cutoff_date:
                    temp = entry.get('temperature')
                    if temp is not None:
                        recent_temps.append(temp)
            
            if recent_temps:
                return sum(recent_temps) / len(recent_temps)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error calculating average temperature: {e}")
            return None
    
    def _calculate_voltage_health(
        self, 
        battery_data: Dict[str, Any], 
        baseline: Dict[str, Any]
    ) -> Optional[float]:
        """Calculate voltage health percentage.
        
        Args:
            battery_data: Current battery data
            baseline: Baseline battery data
            
        Returns:
            Voltage health percentage or None if not available
        """
        try:
            current_voltage = battery_data.get('voltage')
            design_voltage = baseline.get('design_voltage')
            
            if current_voltage and design_voltage and design_voltage > 0:
                voltage_health = (current_voltage / design_voltage) * 100.0
                return min(120.0, max(0.0, voltage_health))  # Allow up to 120%
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error calculating voltage health: {e}")
            return None
    
    def _calculate_degradation_rate(
        self, 
        battery_id: str, 
        current_health: float, 
        age_months: float
    ) -> float:
        """Calculate battery degradation rate per month.
        
        Args:
            battery_id: Battery identifier
            current_health: Current capacity health percentage
            age_months: Battery age in months
            
        Returns:
            Degradation rate as percentage per month
        """
        try:
            if age_months <= 0:
                return 0.0
            
            # Calculate degradation from baseline
            capacity_lost = 100.0 - current_health
            degradation_rate = capacity_lost / age_months
            
            # Smooth the rate using historical data
            history = self._health_history.get(battery_id, [])
            if len(history) >= 2:
                # Calculate trend from recent history
                recent_history = history[-10:]  # Last 10 data points
                if len(recent_history) >= 2:
                    first_entry = recent_history[0]
                    last_entry = recent_history[-1]
                    
                    first_date = datetime.fromisoformat(first_entry['timestamp'])
                    last_date = datetime.fromisoformat(last_entry['timestamp'])
                    
                    time_diff_months = (last_date - first_date).days / 30.44
                    
                    if time_diff_months > 0:
                        first_health = first_entry.get('capacity_health', 100.0)
                        last_health = last_entry.get('capacity_health', 100.0)
                        
                        recent_degradation = (first_health - last_health) / time_diff_months
                        
                        # Weighted average of overall and recent degradation
                        degradation_rate = (degradation_rate + recent_degradation) / 2.0
            
            return max(0.0, degradation_rate)
            
        except Exception as e:
            self.logger.error(f"Error calculating degradation rate: {e}")
            return 0.0
    
    def _estimate_remaining_lifespan(
        self, 
        current_health: float, 
        degradation_rate: float, 
        cycle_count: int
    ) -> Optional[float]:
        """Estimate remaining battery lifespan in months.
        
        Args:
            current_health: Current capacity health percentage
            degradation_rate: Degradation rate per month
            cycle_count: Current cycle count
            
        Returns:
            Estimated remaining lifespan in months or None
        """
        try:
            if degradation_rate <= 0:
                return None
            
            # Calculate months until health drops to 50% (typical replacement threshold)
            replacement_threshold = 50.0
            health_to_lose = current_health - replacement_threshold
            
            if health_to_lose <= 0:
                return 0.0  # Already below replacement threshold
            
            months_remaining = health_to_lose / degradation_rate
            
            # Also consider cycle-based lifespan
            model = self._degradation_models.get('default', {})
            expected_cycles = model.get('expected_lifespan_cycles', 1000)
            
            if cycle_count > 0:
                cycles_remaining = expected_cycles - cycle_count
                if cycles_remaining <= 0:
                    return 0.0
                
                # Estimate months based on current cycle rate
                # Assume average of 1 cycle per 2 days for typical usage
                cycle_based_months = cycles_remaining * 2 / 30.44
                
                # Use the more conservative estimate
                months_remaining = min(months_remaining, cycle_based_months)
            
            return max(0.0, months_remaining)
            
        except Exception as e:
            self.logger.error(f"Error estimating remaining lifespan: {e}")
            return None
    
    def _determine_health_status(
        self, 
        capacity_health: float, 
        cycle_count: int, 
        age_months: float
    ) -> BatteryHealthStatus:
        """Determine overall battery health status.
        
        Args:
            capacity_health: Capacity health percentage
            cycle_count: Current cycle count
            age_months: Battery age in months
            
        Returns:
            BatteryHealthStatus enum value
        """
        try:
            # Primary determination based on capacity health
            for status, threshold in self.health_thresholds.items():
                if capacity_health >= threshold:
                    health_status = status
                    break
            else:
                health_status = BatteryHealthStatus.CRITICAL
            
            # Adjust based on cycle count
            if cycle_count > 1200:
                if health_status.value in ['excellent', 'good']:
                    health_status = BatteryHealthStatus.FAIR
            elif cycle_count > 1000:
                if health_status == BatteryHealthStatus.EXCELLENT:
                    health_status = BatteryHealthStatus.GOOD
            
            # Adjust based on age
            if age_months > 48:  # 4 years
                if health_status.value in ['excellent', 'good']:
                    health_status = BatteryHealthStatus.FAIR
            elif age_months > 36:  # 3 years
                if health_status == BatteryHealthStatus.EXCELLENT:
                    health_status = BatteryHealthStatus.GOOD
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Error determining health status: {e}")
            return BatteryHealthStatus.UNKNOWN
    
    def _generate_health_recommendations(
        self, 
        capacity_health: float, 
        cycle_count: int, 
        temperature_avg: Optional[float], 
        degradation_rate: float
    ) -> List[str]:
        """Generate health-based recommendations.
        
        Args:
            capacity_health: Capacity health percentage
            cycle_count: Current cycle count
            temperature_avg: Average temperature
            degradation_rate: Degradation rate per month
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        try:
            # Capacity-based recommendations
            if capacity_health < 50:
                recommendations.append(
                    "Consider replacing battery - capacity is critically low"
                )
            elif capacity_health < 70:
                recommendations.append(
                    "Battery replacement recommended - capacity significantly degraded"
                )
            elif capacity_health < 85:
                recommendations.append(
                    "Monitor battery closely - showing signs of degradation"
                )
            
            # Cycle-based recommendations
            if cycle_count > 1000:
                recommendations.append(
                    "High cycle count - consider battery replacement soon"
                )
            elif cycle_count > 800:
                recommendations.append(
                    "Moderate cycle count - monitor battery health regularly"
                )
            
            # Temperature-based recommendations
            if temperature_avg and temperature_avg > 35:
                recommendations.append(
                    "Battery running hot - ensure adequate cooling and ventilation"
                )
            elif temperature_avg and temperature_avg > 30:
                recommendations.append(
                    "Monitor battery temperature - avoid high-performance tasks when hot"
                )
            
            # Degradation rate recommendations
            if degradation_rate > 0.5:
                recommendations.append(
                    "Rapid degradation detected - review charging habits and usage patterns"
                )
            elif degradation_rate > 0.3:
                recommendations.append(
                    "Moderate degradation rate - consider optimizing charging patterns"
                )
            
            # General recommendations
            if not recommendations:
                recommendations.extend([
                    "Battery health is good - maintain current usage patterns",
                    "Avoid deep discharges and extreme temperatures for optimal lifespan"
                ])
            else:
                recommendations.extend([
                    "Avoid charging to 100% regularly if possible",
                    "Keep battery between 20-80% charge for optimal lifespan",
                    "Avoid extreme temperatures during charging and storage"
                ])
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            recommendations = ["Unable to generate recommendations due to analysis error"]
        
        return recommendations
    
    def _generate_recommendations(
        self, 
        metrics: BatteryHealthMetrics, 
        battery_data: Dict[str, Any]
    ) -> List[str]:
        """Generate comprehensive recommendations based on health metrics.
        
        Args:
            metrics: Battery health metrics
            battery_data: Current battery data
            
        Returns:
            List of recommendation strings
        """
        return metrics.recommendations
    
    def _store_health_data_point(
        self, 
        battery_id: str, 
        battery_data: Dict[str, Any], 
        metrics: BatteryHealthMetrics
    ) -> None:
        """Store a health data point for historical tracking.
        
        Args:
            battery_id: Battery identifier
            battery_data: Current battery data
            metrics: Calculated health metrics
        """
        try:
            if battery_id not in self._health_history:
                self._health_history[battery_id] = []
            
            data_point = {
                'timestamp': datetime.now().isoformat(),
                'capacity_health': metrics.capacity_health,
                'cycle_count': metrics.cycle_count,
                'charge_percent': battery_data.get('percent'),
                'temperature': battery_data.get('temperature'),
                'voltage': battery_data.get('voltage'),
                'current': battery_data.get('current'),
                'power_plugged': battery_data.get('power_plugged'),
                'degradation_rate': metrics.degradation_rate
            }
            
            self._health_history[battery_id].append(data_point)
            
            # Limit history size (keep last 1000 points per battery)
            if len(self._health_history[battery_id]) > 1000:
                self._health_history[battery_id] = (
                    self._health_history[battery_id][-1000:]
                )
            
            # Save to disk periodically
            if len(self._health_history[battery_id]) % 10 == 0:
                self._save_health_data()
                
        except Exception as e:
            self.logger.error(f"Error storing health data point: {e}")
    
    def _load_health_data(self) -> None:
        """Load health data from disk."""
        try:
            if os.path.exists(self._health_data_file):
                with open(self._health_data_file, 'r') as f:
                    data = json.load(f)
                    self._health_history = data.get('health_history', {})
                    self._baseline_data = data.get('baseline_data', {})
                    
                self.logger.info("Loaded battery health data from disk")
            else:
                self.logger.info("No existing health data found")
                
        except Exception as e:
            self.logger.error(f"Error loading health data: {e}")
            self._health_history = {}
            self._baseline_data = {}
    
    def _save_health_data(self) -> None:
        """Save health data to disk."""
        try:
            data = {
                'health_history': self._health_history,
                'baseline_data': self._baseline_data,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self._health_data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving health data: {e}")
    
    def get_health_trend(
        self, 
        battery_id: str, 
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get health trend data for a battery.
        
        Args:
            battery_id: Battery identifier
            days: Number of days of trend data to retrieve
            
        Returns:
            List of health trend data points
        """
        try:
            if battery_id not in self._health_history:
                return []
            
            cutoff_date = datetime.now() - timedelta(days=days)
            trend_data = []
            
            for entry in self._health_history[battery_id]:
                entry_date = datetime.fromisoformat(entry['timestamp'])
                if entry_date > cutoff_date:
                    trend_data.append(entry)
            
            return trend_data
            
        except Exception as e:
            self.logger.error(f"Error getting health trend for {battery_id}: {e}")
            return []
    
    def get_degradation_prediction(
        self, 
        battery_id: str, 
        months_ahead: int = 12
    ) -> Dict[str, Any]:
        """Predict battery degradation for future months.
        
        Args:
            battery_id: Battery identifier
            months_ahead: Number of months to predict ahead
            
        Returns:
            Dict containing degradation predictions
        """
        try:
            if battery_id not in self._health_history:
                return {}
            
            history = self._health_history[battery_id]
            if len(history) < 2:
                return {}
            
            # Calculate current degradation rate
            recent_entries = history[-10:]  # Last 10 entries
            if len(recent_entries) < 2:
                return {}
            
            first_entry = recent_entries[0]
            last_entry = recent_entries[-1]
            
            first_date = datetime.fromisoformat(first_entry['timestamp'])
            last_date = datetime.fromisoformat(last_entry['timestamp'])
            
            time_diff_months = (last_date - first_date).days / 30.44
            
            if time_diff_months <= 0:
                return {}
            
            first_health = first_entry.get('capacity_health', 100.0)
            last_health = last_entry.get('capacity_health', 100.0)
            
            degradation_rate = (first_health - last_health) / time_diff_months
            
            # Generate predictions
            predictions = []
            current_health = last_health
            
            for month in range(1, months_ahead + 1):
                predicted_health = current_health - (degradation_rate * month)
                predicted_health = max(0.0, predicted_health)
                
                predictions.append({
                    'month': month,
                    'predicted_health': predicted_health,
                    'predicted_date': (
                        datetime.now() + timedelta(days=month * 30.44)
                    ).isoformat()
                })
            
            return {
                'battery_id': battery_id,
                'current_health': last_health,
                'degradation_rate_per_month': degradation_rate,
                'predictions': predictions
            }
            
        except Exception as e:
            self.logger.error(
                f"Error generating degradation prediction for {battery_id}: {e}"
            )
            return {}