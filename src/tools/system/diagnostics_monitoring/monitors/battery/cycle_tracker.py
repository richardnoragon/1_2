"""Charge cycle tracking and battery lifespan analysis."""

import logging
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ...core.platform_detector import get_platform_detector
from core.error_handler import error_handler


class ChargingPhase(Enum):
    """Battery charging phases."""

    DISCHARGING = "discharging"
    CHARGING = "charging"
    FULL = "full"
    UNKNOWN = "unknown"


@dataclass
class ChargeCycle:
    """Represents a complete charge cycle."""

    start_time: datetime
    end_time: Optional[datetime]
    start_percent: float
    end_percent: float
    depth_of_discharge: float
    charging_time_minutes: Optional[float]
    temperature_avg: Optional[float]
    voltage_avg: Optional[float]
    cycle_efficiency: Optional[float]
    is_complete: bool


@dataclass
class ChargingSession:
    """Represents a charging session."""

    start_time: datetime
    end_time: Optional[datetime]
    start_percent: float
    end_percent: Optional[float]
    peak_temperature: Optional[float]
    charging_rate: Optional[float]
    power_consumption: Optional[float]
    session_type: str  # "partial", "full", "maintenance"


class ChargeCycleTracker:
    """Tracks battery charge cycles and analyzes charging patterns."""

    def __init__(self):
        """Initialize the charge cycle tracker."""
        self.logger = logging.getLogger(
            "RFU.DiagnosticsMonitoring.ChargeCycleTracker"
        )
        self.platform_detector = get_platform_detector()

        # Cycle tracking data
        self._cycles: Dict[str, List[ChargeCycle]] = {}
        self._charging_sessions: Dict[str, List[ChargingSession]] = {}
        self._current_sessions: Dict[str, ChargingSession] = {}
        self._battery_states: Dict[str, Dict[str, Any]] = {}

        # Configuration
        self._config_dir = self.platform_detector.get_config_directory()
        self._cycle_data_file = os.path.join(
            self._config_dir, "battery_cycles.json"
        )

        # Cycle calculation parameters
        self.min_discharge_depth = 20.0  # Minimum discharge for cycle counting
        self.cycle_completion_threshold = 80.0  # % charge for cycle completion
        self.partial_cycle_weight = 0.5  # Weight for partial cycles

        # Load existing cycle data
        self._load_cycle_data()

        self.logger.info("Charge cycle tracker initialized")

    def initialize(self) -> None:
        """Initialize the cycle tracker."""
        try:
            # Create config directory if it doesn't exist
            os.makedirs(self._config_dir, exist_ok=True)

            self.logger.info("Cycle tracker initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize cycle tracker: {e}")
            error_handler.handle_error(e, "ChargeCycleTracker.initialize")

    def track_charging_event(
        self,
        battery_id: str,
        is_charging: bool,
        charge_percent: float,
        timestamp: datetime,
        temperature: Optional[float] = None,
        voltage: Optional[float] = None,
        current: Optional[float] = None,
    ) -> None:
        """Track a charging state change event.

        Args:
            battery_id: Battery identifier
            is_charging: Whether battery is currently charging
            charge_percent: Current charge percentage
            timestamp: Event timestamp
            temperature: Battery temperature (optional)
            voltage: Battery voltage (optional)
            current: Battery current (optional)
        """
        try:
            # Initialize battery tracking if needed
            if battery_id not in self._battery_states:
                self._battery_states[battery_id] = {
                    "last_charge_percent": charge_percent,
                    "last_charging_state": is_charging,
                    "last_timestamp": timestamp,
                    "phase": ChargingPhase.UNKNOWN,
                    "cycle_start_percent": None,
                    "cycle_start_time": None,
                }

            state = self._battery_states[battery_id]
            last_charging = state["last_charging_state"]
            last_percent = state["last_charge_percent"]

            # Detect charging state transitions
            if is_charging and not last_charging:
                # Started charging
                self._handle_charging_start(
                    battery_id,
                    charge_percent,
                    timestamp,
                    temperature,
                    voltage,
                    current,
                )
            elif not is_charging and last_charging:
                # Stopped charging
                self._handle_charging_stop(
                    battery_id,
                    charge_percent,
                    timestamp,
                    temperature,
                    voltage,
                    current,
                )
            elif is_charging:
                # Continue charging
                self._update_charging_session(
                    battery_id,
                    charge_percent,
                    timestamp,
                    temperature,
                    voltage,
                    current,
                )
            else:
                # Continue discharging
                self._update_discharging(
                    battery_id,
                    charge_percent,
                    timestamp,
                    temperature,
                    voltage,
                    current,
                )

            # Update state
            state.update(
                {
                    "last_charge_percent": charge_percent,
                    "last_charging_state": is_charging,
                    "last_timestamp": timestamp,
                }
            )

            # Check for cycle completion
            self._check_cycle_completion(battery_id, charge_percent, timestamp)

        except Exception as e:
            self.logger.error(f"Error tracking charging event: {e}")

    def _handle_charging_start(
        self,
        battery_id: str,
        charge_percent: float,
        timestamp: datetime,
        temperature: Optional[float],
        voltage: Optional[float],
        current: Optional[float],
    ) -> None:
        """Handle the start of a charging session.

        Args:
            battery_id: Battery identifier
            charge_percent: Current charge percentage
            timestamp: Event timestamp
            temperature: Battery temperature
            voltage: Battery voltage
            current: Battery current
        """
        try:
            # Start new charging session
            session = ChargingSession(
                start_time=timestamp,
                end_time=None,
                start_percent=charge_percent,
                end_percent=None,
                peak_temperature=temperature,
                charging_rate=None,
                power_consumption=None,
                session_type="partial",
            )

            self._current_sessions[battery_id] = session

            # Update battery phase
            self._battery_states[battery_id]["phase"] = ChargingPhase.CHARGING

            self.logger.debug(
                f"Started charging session for {battery_id} at {charge_percent}%"
            )

        except Exception as e:
            self.logger.error(f"Error handling charging start: {e}")

    def _handle_charging_stop(
        self,
        battery_id: str,
        charge_percent: float,
        timestamp: datetime,
        temperature: Optional[float],
        voltage: Optional[float],
        current: Optional[float],
    ) -> None:
        """Handle the end of a charging session.

        Args:
            battery_id: Battery identifier
            charge_percent: Current charge percentage
            timestamp: Event timestamp
            temperature: Battery temperature
            voltage: Battery voltage
            current: Battery current
        """
        try:
            # Complete current charging session
            if battery_id in self._current_sessions:
                session = self._current_sessions[battery_id]
                session.end_time = timestamp
                session.end_percent = charge_percent

                # Calculate session metrics
                if session.start_percent is not None:
                    charge_gained = charge_percent - session.start_percent
                    session_duration = (
                        timestamp - session.start_time
                    ).total_seconds() / 60.0

                    if session_duration > 0:
                        session.charging_rate = (
                            charge_gained / session_duration
                        )

                    # Determine session type
                    if charge_percent >= 95:
                        session.session_type = "full"
                    elif charge_gained >= 50:
                        session.session_type = "partial"
                    else:
                        session.session_type = "maintenance"

                # Store completed session
                if battery_id not in self._charging_sessions:
                    self._charging_sessions[battery_id] = []

                self._charging_sessions[battery_id].append(session)

                # Limit session history
                if len(self._charging_sessions[battery_id]) > 500:
                    self._charging_sessions[battery_id] = (
                        self._charging_sessions[battery_id][-500:]
                    )

                del self._current_sessions[battery_id]

            # Update battery phase
            if charge_percent >= 95:
                self._battery_states[battery_id]["phase"] = ChargingPhase.FULL
            else:
                self._battery_states[battery_id][
                    "phase"
                ] = ChargingPhase.DISCHARGING

            self.logger.debug(
                f"Stopped charging session for {battery_id} at {charge_percent}%"
            )

        except Exception as e:
            self.logger.error(f"Error handling charging stop: {e}")

    def _update_charging_session(
        self,
        battery_id: str,
        charge_percent: float,
        timestamp: datetime,
        temperature: Optional[float],
        voltage: Optional[float],
        current: Optional[float],
    ) -> None:
        """Update ongoing charging session.

        Args:
            battery_id: Battery identifier
            charge_percent: Current charge percentage
            timestamp: Event timestamp
            temperature: Battery temperature
            voltage: Battery voltage
            current: Battery current
        """
        try:
            if battery_id in self._current_sessions:
                session = self._current_sessions[battery_id]

                # Update peak temperature
                if temperature is not None:
                    if session.peak_temperature is None:
                        session.peak_temperature = temperature
                    else:
                        session.peak_temperature = max(
                            session.peak_temperature, temperature
                        )

                # Calculate power consumption if voltage and current available
                if voltage is not None and current is not None:
                    power_w = abs(
                        voltage * current / 1000.0
                    )  # Convert mA to A
                    session.power_consumption = power_w

        except Exception as e:
            self.logger.error(f"Error updating charging session: {e}")

    def _update_discharging(
        self,
        battery_id: str,
        charge_percent: float,
        timestamp: datetime,
        temperature: Optional[float],
        voltage: Optional[float],
        current: Optional[float],
    ) -> None:
        """Update discharging state.

        Args:
            battery_id: Battery identifier
            charge_percent: Current charge percentage
            timestamp: Event timestamp
            temperature: Battery temperature
            voltage: Battery voltage
            current: Battery current
        """
        try:
            state = self._battery_states[battery_id]

            # Check if we should start tracking a new cycle
            if state.get("cycle_start_percent") is None:
                # Start tracking from a high charge level
                if charge_percent >= 80:
                    state["cycle_start_percent"] = charge_percent
                    state["cycle_start_time"] = timestamp

            # Update phase
            state["phase"] = ChargingPhase.DISCHARGING

        except Exception as e:
            self.logger.error(f"Error updating discharging state: {e}")

    def _check_cycle_completion(
        self, battery_id: str, charge_percent: float, timestamp: datetime
    ) -> None:
        """Check if a charge cycle has been completed.

        Args:
            battery_id: Battery identifier
            charge_percent: Current charge percentage
            timestamp: Event timestamp
        """
        try:
            state = self._battery_states[battery_id]
            cycle_start_percent = state.get("cycle_start_percent")
            cycle_start_time = state.get("cycle_start_time")

            if cycle_start_percent is None or cycle_start_time is None:
                return

            # Check if we've completed a significant discharge and recharge
            if (
                state["phase"] == ChargingPhase.CHARGING
                and charge_percent >= self.cycle_completion_threshold
            ):

                # Calculate depth of discharge
                min_percent = self._get_minimum_charge_in_cycle(
                    battery_id, cycle_start_time, timestamp
                )

                if min_percent is not None:
                    depth_of_discharge = cycle_start_percent - min_percent

                    if depth_of_discharge >= self.min_discharge_depth:
                        # Complete cycle detected
                        cycle = ChargeCycle(
                            start_time=cycle_start_time,
                            end_time=timestamp,
                            start_percent=cycle_start_percent,
                            end_percent=charge_percent,
                            depth_of_discharge=depth_of_discharge,
                            charging_time_minutes=None,
                            temperature_avg=None,
                            voltage_avg=None,
                            cycle_efficiency=None,
                            is_complete=True,
                        )

                        # Calculate additional metrics
                        self._calculate_cycle_metrics(battery_id, cycle)

                        # Store cycle
                        if battery_id not in self._cycles:
                            self._cycles[battery_id] = []

                        self._cycles[battery_id].append(cycle)

                        # Limit cycle history
                        if len(self._cycles[battery_id]) > 1000:
                            self._cycles[battery_id] = self._cycles[
                                battery_id
                            ][-1000:]

                        # Reset cycle tracking
                        state["cycle_start_percent"] = charge_percent
                        state["cycle_start_time"] = timestamp

                        self.logger.info(
                            f"Completed cycle for {battery_id}: "
                            f"{depth_of_discharge:.1f}% depth of discharge"
                        )

                        # Save cycle data
                        self._save_cycle_data()

        except Exception as e:
            self.logger.error(f"Error checking cycle completion: {e}")

    def _get_minimum_charge_in_cycle(
        self, battery_id: str, start_time: datetime, end_time: datetime
    ) -> Optional[float]:
        """Get the minimum charge level during a cycle period.

        Args:
            battery_id: Battery identifier
            start_time: Cycle start time
            end_time: Cycle end time

        Returns:
            Minimum charge percentage or None if not found
        """
        try:
            # This would ideally use historical data points
            # For now, estimate based on current state
            state = self._battery_states.get(battery_id, {})
            last_percent = state.get("last_charge_percent", 100.0)

            # Simple estimation - in a real implementation, this would
            # analyze stored data points during the cycle period
            return last_percent

        except Exception as e:
            self.logger.error(f"Error getting minimum charge in cycle: {e}")
            return None

    def _calculate_cycle_metrics(
        self, battery_id: str, cycle: ChargeCycle
    ) -> None:
        """Calculate additional metrics for a completed cycle.

        Args:
            battery_id: Battery identifier
            cycle: Charge cycle to calculate metrics for
        """
        try:
            # Calculate charging time from sessions
            if battery_id in self._charging_sessions:
                relevant_sessions = []
                for session in self._charging_sessions[battery_id]:
                    if (
                        session.start_time >= cycle.start_time
                        and session.end_time
                        and session.end_time <= cycle.end_time
                    ):
                        relevant_sessions.append(session)

                if relevant_sessions:
                    total_charging_time = sum(
                        (session.end_time - session.start_time).total_seconds()
                        / 60.0
                        for session in relevant_sessions
                        if session.end_time
                    )
                    cycle.charging_time_minutes = total_charging_time

                    # Calculate average temperature during charging
                    temps = [
                        session.peak_temperature
                        for session in relevant_sessions
                        if session.peak_temperature is not None
                    ]
                    if temps:
                        cycle.temperature_avg = sum(temps) / len(temps)

                    # Calculate cycle efficiency (simplified)
                    if (
                        cycle.charging_time_minutes
                        and cycle.charging_time_minutes > 0
                    ):
                        # Efficiency based on charge gained vs time
                        charge_gained = cycle.end_percent - (
                            cycle.start_percent - cycle.depth_of_discharge
                        )
                        if charge_gained > 0:
                            cycle.cycle_efficiency = min(
                                100.0,
                                (charge_gained / cycle.charging_time_minutes)
                                * 60.0,
                            )

        except Exception as e:
            self.logger.error(f"Error calculating cycle metrics: {e}")

    def get_cycle_data(self, battery_id: str) -> Dict[str, Any]:
        """Get cycle tracking data for a battery.

        Args:
            battery_id: Battery identifier

        Returns:
            Dict containing cycle data
        """
        try:
            cycles = self._cycles.get(battery_id, [])
            sessions = self._charging_sessions.get(battery_id, [])

            # Calculate cycle statistics
            total_cycles = len(cycles)

            if cycles:
                avg_depth = (
                    sum(cycle.depth_of_discharge for cycle in cycles)
                    / total_cycles
                )
                avg_charging_time = None

                charging_times = [
                    cycle.charging_time_minutes
                    for cycle in cycles
                    if cycle.charging_time_minutes is not None
                ]
                if charging_times:
                    avg_charging_time = sum(charging_times) / len(
                        charging_times
                    )

                # Recent cycle analysis (last 10 cycles)
                recent_cycles = cycles[-10:] if len(cycles) >= 10 else cycles
                recent_avg_depth = sum(
                    cycle.depth_of_discharge for cycle in recent_cycles
                ) / len(recent_cycles)

                # Calculate cycle degradation trend
                degradation_trend = self._calculate_cycle_degradation_trend(
                    cycles
                )
            else:
                avg_depth = 0.0
                avg_charging_time = None
                recent_avg_depth = 0.0
                degradation_trend = 0.0

            # Recent charging session analysis
            recent_sessions = (
                sessions[-30:] if len(sessions) >= 30 else sessions
            )
            session_stats = self._analyze_charging_sessions(recent_sessions)

            return {
                "cycle_count": total_cycles,
                "average_depth_of_discharge": avg_depth,
                "recent_average_depth": recent_avg_depth,
                "average_charging_time_minutes": avg_charging_time,
                "cycle_degradation_trend": degradation_trend,
                "total_charging_sessions": len(sessions),
                "recent_session_stats": session_stats,
                "last_cycle_date": (
                    cycles[-1].end_time.isoformat()
                    if cycles and cycles[-1].end_time
                    else None
                ),
                "cycle_efficiency_avg": self._calculate_average_efficiency(
                    cycles
                ),
            }

        except Exception as e:
            self.logger.error(
                f"Error getting cycle data for {battery_id}: {e}"
            )
            return {}

    def _calculate_cycle_degradation_trend(
        self, cycles: List[ChargeCycle]
    ) -> float:
        """Calculate the degradation trend from cycle data.

        Args:
            cycles: List of charge cycles

        Returns:
            Degradation trend (positive = degrading)
        """
        try:
            if len(cycles) < 5:
                return 0.0

            # Analyze efficiency trend over recent cycles
            recent_cycles = cycles[-20:] if len(cycles) >= 20 else cycles

            efficiencies = [
                cycle.cycle_efficiency
                for cycle in recent_cycles
                if cycle.cycle_efficiency is not None
            ]

            if len(efficiencies) < 3:
                return 0.0

            # Simple linear trend calculation
            n = len(efficiencies)
            x_avg = (n - 1) / 2.0
            y_avg = sum(efficiencies) / n

            numerator = sum(
                (i - x_avg) * (efficiencies[i] - y_avg) for i in range(n)
            )
            denominator = sum((i - x_avg) ** 2 for i in range(n))

            if denominator == 0:
                return 0.0

            slope = numerator / denominator
            return -slope  # Negative slope indicates degradation

        except Exception as e:
            self.logger.error(f"Error calculating degradation trend: {e}")
            return 0.0

    def _analyze_charging_sessions(
        self, sessions: List[ChargingSession]
    ) -> Dict[str, Any]:
        """Analyze charging session statistics.

        Args:
            sessions: List of charging sessions

        Returns:
            Dict containing session analysis
        """
        try:
            if not sessions:
                return {}

            # Session type distribution
            session_types = {}
            charging_rates = []
            peak_temperatures = []

            for session in sessions:
                session_type = session.session_type
                session_types[session_type] = (
                    session_types.get(session_type, 0) + 1
                )

                if session.charging_rate is not None:
                    charging_rates.append(session.charging_rate)

                if session.peak_temperature is not None:
                    peak_temperatures.append(session.peak_temperature)

            analysis = {
                "session_type_distribution": session_types,
                "total_sessions": len(sessions),
                "average_charging_rate": (
                    sum(charging_rates) / len(charging_rates)
                    if charging_rates
                    else None
                ),
                "average_peak_temperature": (
                    sum(peak_temperatures) / len(peak_temperatures)
                    if peak_temperatures
                    else None
                ),
                "max_peak_temperature": (
                    max(peak_temperatures) if peak_temperatures else None
                ),
            }

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing charging sessions: {e}")
            return {}

    def _calculate_average_efficiency(
        self, cycles: List[ChargeCycle]
    ) -> Optional[float]:
        """Calculate average cycle efficiency.

        Args:
            cycles: List of charge cycles

        Returns:
            Average efficiency percentage or None
        """
        try:
            efficiencies = [
                cycle.cycle_efficiency
                for cycle in cycles
                if cycle.cycle_efficiency is not None
            ]

            if efficiencies:
                return sum(efficiencies) / len(efficiencies)

            return None

        except Exception as e:
            self.logger.error(f"Error calculating average efficiency: {e}")
            return None

    def get_cycle_history(
        self, battery_id: str, days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get cycle history for a battery.

        Args:
            battery_id: Battery identifier
            days: Number of days of history to retrieve

        Returns:
            List of cycle data
        """
        try:
            if battery_id not in self._cycles:
                return []

            cutoff_date = datetime.now() - timedelta(days=days)
            recent_cycles = []

            for cycle in self._cycles[battery_id]:
                if cycle.start_time > cutoff_date:
                    cycle_data = {
                        "start_time": cycle.start_time.isoformat(),
                        "end_time": (
                            cycle.end_time.isoformat()
                            if cycle.end_time
                            else None
                        ),
                        "depth_of_discharge": cycle.depth_of_discharge,
                        "charging_time_minutes": cycle.charging_time_minutes,
                        "temperature_avg": cycle.temperature_avg,
                        "cycle_efficiency": cycle.cycle_efficiency,
                        "is_complete": cycle.is_complete,
                    }
                    recent_cycles.append(cycle_data)

            return recent_cycles

        except Exception as e:
            self.logger.error(
                f"Error getting cycle history for {battery_id}: {e}"
            )
            return []

    def get_charging_pattern_analysis(self, battery_id: str) -> Dict[str, Any]:
        """Analyze charging patterns for optimization recommendations.

        Args:
            battery_id: Battery identifier

        Returns:
            Dict containing charging pattern analysis
        """
        try:
            sessions = self._charging_sessions.get(battery_id, [])
            if not sessions:
                return {}

            # Analyze recent sessions (last 30 days)
            cutoff_date = datetime.now() - timedelta(days=30)
            recent_sessions = [
                session
                for session in sessions
                if session.start_time > cutoff_date
            ]

            if not recent_sessions:
                return {}

            # Charging time analysis
            charging_times = []
            for session in recent_sessions:
                if session.end_time:
                    duration = (
                        session.end_time - session.start_time
                    ).total_seconds() / 3600.0
                    charging_times.append(duration)

            # Charging level analysis
            start_levels = [
                session.start_percent for session in recent_sessions
            ]
            end_levels = [
                session.end_percent
                for session in recent_sessions
                if session.end_percent is not None
            ]

            # Temperature analysis
            peak_temps = [
                session.peak_temperature
                for session in recent_sessions
                if session.peak_temperature is not None
            ]

            # Generate recommendations
            recommendations = self._generate_charging_recommendations(
                recent_sessions,
                charging_times,
                start_levels,
                end_levels,
                peak_temps,
            )

            analysis = {
                "total_sessions_analyzed": len(recent_sessions),
                "average_charging_time_hours": (
                    sum(charging_times) / len(charging_times)
                    if charging_times
                    else None
                ),
                "average_start_level": (
                    sum(start_levels) / len(start_levels)
                    if start_levels
                    else None
                ),
                "average_end_level": (
                    sum(end_levels) / len(end_levels) if end_levels else None
                ),
                "average_peak_temperature": (
                    sum(peak_temps) / len(peak_temps) if peak_temps else None
                ),
                "session_type_distribution": self._analyze_charging_sessions(
                    recent_sessions
                ).get("session_type_distribution", {}),
                "recommendations": recommendations,
            }

            return analysis

        except Exception as e:
            self.logger.error(
                f"Error analyzing charging patterns for {battery_id}: {e}"
            )
            return {}

    def _generate_charging_recommendations(
        self,
        sessions: List[ChargingSession],
        charging_times: List[float],
        start_levels: List[float],
        end_levels: List[float],
        peak_temps: List[float],
    ) -> List[str]:
        """Generate charging optimization recommendations.

        Args:
            sessions: Recent charging sessions
            charging_times: Charging time durations
            start_levels: Session start charge levels
            end_levels: Session end charge levels
            peak_temps: Peak temperatures during charging

        Returns:
            List of recommendation strings
        """
        recommendations = []

        try:
            # Analyze charging patterns
            if start_levels:
                avg_start = sum(start_levels) / len(start_levels)
                if avg_start < 20:
                    recommendations.append(
                        "Consider charging before battery drops below 20% for optimal lifespan"
                    )

            if end_levels:
                avg_end = sum(end_levels) / len(end_levels)
                if avg_end > 90:
                    recommendations.append(
                        "Consider limiting charge to 80-90% for daily use to reduce stress"
                    )

            if peak_temps:
                avg_temp = sum(peak_temps) / len(peak_temps)
                if avg_temp > 35:
                    recommendations.append(
                        "Battery temperature is high during charging - ensure good ventilation"
                    )
                elif avg_temp > 30:
                    recommendations.append(
                        "Monitor charging temperature - avoid charging in hot environments"
                    )

            if charging_times:
                avg_time = sum(charging_times) / len(charging_times)
                if avg_time > 4:
                    recommendations.append(
                        "Long charging times detected - consider using faster charger if available"
                    )

            # Session pattern analysis
            full_sessions = sum(
                1 for s in sessions if s.session_type == "full"
            )
            total_sessions = len(sessions)

            if total_sessions > 0:
                full_ratio = full_sessions / total_sessions
                if full_ratio > 0.8:
                    recommendations.append(
                        "Frequent full charges detected - consider partial charging for daily use"
                    )
                elif full_ratio < 0.2:
                    recommendations.append(
                        "Consider occasional full charge cycles for battery calibration"
                    )

            if not recommendations:
                recommendations.append(
                    "Charging patterns look optimal - continue current habits"
                )

        except Exception as e:
            self.logger.error(
                f"Error generating charging recommendations: {e}"
            )
            recommendations = [
                "Unable to generate recommendations due to analysis error"
            ]

        return recommendations

    def _load_cycle_data(self) -> None:
        """Load cycle data from disk."""
        try:
            if os.path.exists(self._cycle_data_file):
                with open(self._cycle_data_file, "r") as f:
                    data = json.load(f)

                    # Load cycles
                    cycles_data = data.get("cycles", {})
                    for battery_id, cycle_list in cycles_data.items():
                        self._cycles[battery_id] = []
                        for cycle_data in cycle_list:
                            cycle = ChargeCycle(
                                start_time=datetime.fromisoformat(
                                    cycle_data["start_time"]
                                ),
                                end_time=(
                                    datetime.fromisoformat(
                                        cycle_data["end_time"]
                                    )
                                    if cycle_data.get("end_time")
                                    else None
                                ),
                                start_percent=cycle_data["start_percent"],
                                end_percent=cycle_data["end_percent"],
                                depth_of_discharge=cycle_data[
                                    "depth_of_discharge"
                                ],
                                charging_time_minutes=cycle_data.get(
                                    "charging_time_minutes"
                                ),
                                temperature_avg=cycle_data.get(
                                    "temperature_avg"
                                ),
                                voltage_avg=cycle_data.get("voltage_avg"),
                                cycle_efficiency=cycle_data.get(
                                    "cycle_efficiency"
                                ),
                                is_complete=cycle_data.get(
                                    "is_complete", True
                                ),
                            )
                            self._cycles[battery_id].append(cycle)

                    # Load charging sessions
                    sessions_data = data.get("charging_sessions", {})
                    for battery_id, session_list in sessions_data.items():
                        self._charging_sessions[battery_id] = []
                        for session_data in session_list:
                            session = ChargingSession(
                                start_time=datetime.fromisoformat(
                                    session_data["start_time"]
                                ),
                                end_time=(
                                    datetime.fromisoformat(
                                        session_data["end_time"]
                                    )
                                    if session_data.get("end_time")
                                    else None
                                ),
                                start_percent=session_data["start_percent"],
                                end_percent=session_data.get("end_percent"),
                                peak_temperature=session_data.get(
                                    "peak_temperature"
                                ),
                                charging_rate=session_data.get(
                                    "charging_rate"
                                ),
                                power_consumption=session_data.get(
                                    "power_consumption"
                                ),
                                session_type=session_data.get(
                                    "session_type", "partial"
                                ),
                            )
                            self._charging_sessions[battery_id].append(session)

                    # Load battery states
                    self._battery_states = data.get("battery_states", {})

                    # Convert datetime strings back to datetime objects in states
                    for battery_id, state in self._battery_states.items():
                        if "last_timestamp" in state and isinstance(
                            state["last_timestamp"], str
                        ):
                            state["last_timestamp"] = datetime.fromisoformat(
                                state["last_timestamp"]
                            )
                        if "cycle_start_time" in state and isinstance(
                            state["cycle_start_time"], str
                        ):
                            state["cycle_start_time"] = datetime.fromisoformat(
                                state["cycle_start_time"]
                            )
                        if "phase" in state and isinstance(
                            state["phase"], str
                        ):
                            state["phase"] = ChargingPhase(state["phase"])

                self.logger.info("Loaded battery cycle data from disk")
            else:
                self.logger.info("No existing cycle data found")

        except Exception as e:
            self.logger.error(f"Error loading cycle data: {e}")
            self._cycles = {}
            self._charging_sessions = {}
            self._battery_states = {}

    def _save_cycle_data(self) -> None:
        """Save cycle data to disk."""
        try:
            # Prepare data for JSON serialization
            cycles_data = {}
            for battery_id, cycles in self._cycles.items():
                cycles_data[battery_id] = []
                for cycle in cycles:
                    cycle_data = {
                        "start_time": cycle.start_time.isoformat(),
                        "end_time": (
                            cycle.end_time.isoformat()
                            if cycle.end_time
                            else None
                        ),
                        "start_percent": cycle.start_percent,
                        "end_percent": cycle.end_percent,
                        "depth_of_discharge": cycle.depth_of_discharge,
                        "charging_time_minutes": cycle.charging_time_minutes,
                        "temperature_avg": cycle.temperature_avg,
                        "voltage_avg": cycle.voltage_avg,
                        "cycle_efficiency": cycle.cycle_efficiency,
                        "is_complete": cycle.is_complete,
                    }
                    cycles_data[battery_id].append(cycle_data)

            sessions_data = {}
            for battery_id, sessions in self._charging_sessions.items():
                sessions_data[battery_id] = []
                for session in sessions:
                    session_data = {
                        "start_time": session.start_time.isoformat(),
                        "end_time": (
                            session.end_time.isoformat()
                            if session.end_time
                            else None
                        ),
                        "start_percent": session.start_percent,
                        "end_percent": session.end_percent,
                        "peak_temperature": session.peak_temperature,
                        "charging_rate": session.charging_rate,
                        "power_consumption": session.power_consumption,
                        "session_type": session.session_type,
                    }
                    sessions_data[battery_id].append(session_data)

            # Prepare battery states for serialization
            states_data = {}
            for battery_id, state in self._battery_states.items():
                state_copy = state.copy()
                if "last_timestamp" in state_copy and isinstance(
                    state_copy["last_timestamp"], datetime
                ):
                    state_copy["last_timestamp"] = state_copy[
                        "last_timestamp"
                    ].isoformat()
                if "cycle_start_time" in state_copy and isinstance(
                    state_copy["cycle_start_time"], datetime
                ):
                    state_copy["cycle_start_time"] = state_copy[
                        "cycle_start_time"
                    ].isoformat()
                if "phase" in state_copy and isinstance(
                    state_copy["phase"], ChargingPhase
                ):
                    state_copy["phase"] = state_copy["phase"].value
                states_data[battery_id] = state_copy

            data = {
                "cycles": cycles_data,
                "charging_sessions": sessions_data,
                "battery_states": states_data,
                "last_updated": datetime.now().isoformat(),
            }

            with open(self._cycle_data_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error saving cycle data: {e}")
