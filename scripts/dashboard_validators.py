"""
Dashboard Validators for Team Performance Dashboard
Feature 2: Team Performance Dashboard

Validates dashboard data, metrics, and snapshots.
Ensures data quality and consistency across dashboard operations.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class DashboardValidator:
    """Validates dashboard data and metrics."""
    
    # Valid values
    VALID_PERIODS = {"daily", "weekly", "monthly", "real-time"}
    VALID_STATUSES = {"online", "in_session", "paused", "offline"}
    VALID_METRIC_UNITS = {"hours", "tasks", "%", "people", "score", "rate"}
    
    # Min/Max bounds
    MIN_PRODUCTIVITY_SCORE = 0.0
    MAX_PRODUCTIVITY_SCORE = 100.0
    MIN_UTILIZATION_RATE = 0.0
    MAX_UTILIZATION_RATE = 100.0
    
    @staticmethod
    def validate_team_metric(metric_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate team metric data.
        
        Args:
            metric_data: Metric data to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(metric_data, dict):
            return False, "Metric must be a dictionary"
        
        # Check required fields
        required_fields = ["name", "value", "unit", "category"]
        for field in required_fields:
            if field not in metric_data:
                return False, f"Missing required field: {field}"
        
        # Validate name
        if not isinstance(metric_data["name"], str) or not metric_data["name"].strip():
            return False, "Metric name must be non-empty string"
        
        # Validate value
        try:
            value = float(metric_data["value"])
            if value < 0:
                return False, "Metric value cannot be negative"
        except (ValueError, TypeError):
            return False, "Metric value must be numeric"
        
        # Validate unit
        if metric_data["unit"] not in DashboardValidator.VALID_METRIC_UNITS:
            return False, f"Invalid unit: {metric_data['unit']}"
        
        # Validate category
        if not isinstance(metric_data["category"], str) or not metric_data["category"].strip():
            return False, "Category must be non-empty string"
        
        # Validate period if present
        if "period" in metric_data:
            if metric_data["period"] not in DashboardValidator.VALID_PERIODS:
                return False, f"Invalid period: {metric_data['period']}"
        
        # Validate timestamp if present
        if "timestamp" in metric_data:
            if not DashboardValidator._is_valid_iso_timestamp(metric_data["timestamp"]):
                return False, "Invalid timestamp format"
        
        return True, None
    
    @staticmethod
    def validate_employee_pattern(pattern_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate employee work pattern data.
        
        Args:
            pattern_data: Employee pattern data
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(pattern_data, dict):
            return False, "Pattern must be a dictionary"
        
        # Check required fields
        if "employee_id" not in pattern_data:
            return False, "Missing required field: employee_id"
        
        if not isinstance(pattern_data["employee_id"], str) or not pattern_data["employee_id"].strip():
            return False, "employee_id must be non-empty string"
        
        # Validate hours if present
        if "total_hours_logged" in pattern_data:
            try:
                hours = float(pattern_data["total_hours_logged"])
                if hours < 0:
                    return False, "total_hours_logged cannot be negative"
            except (ValueError, TypeError):
                return False, "total_hours_logged must be numeric"
        
        # Validate tasks if present
        if "total_tasks_completed" in pattern_data:
            try:
                tasks = int(pattern_data["total_tasks_completed"])
                if tasks < 0:
                    return False, "total_tasks_completed cannot be negative"
            except (ValueError, TypeError):
                return False, "total_tasks_completed must be integer"
        
        # Validate productivity score
        if "productivity_score" in pattern_data:
            try:
                score = float(pattern_data["productivity_score"])
                if not (DashboardValidator.MIN_PRODUCTIVITY_SCORE <= score <= DashboardValidator.MAX_PRODUCTIVITY_SCORE):
                    return False, f"Productivity score must be between {DashboardValidator.MIN_PRODUCTIVITY_SCORE} and {DashboardValidator.MAX_PRODUCTIVITY_SCORE}"
            except (ValueError, TypeError):
                return False, "productivity_score must be numeric"
        
        # Validate utilization rate
        if "utilization_rate" in pattern_data:
            try:
                rate = float(pattern_data["utilization_rate"])
                if not (DashboardValidator.MIN_UTILIZATION_RATE <= rate <= DashboardValidator.MAX_UTILIZATION_RATE):
                    return False, f"Utilization rate must be between {DashboardValidator.MIN_UTILIZATION_RATE} and {DashboardValidator.MAX_UTILIZATION_RATE}"
            except (ValueError, TypeError):
                return False, "utilization_rate must be numeric"
        
        # Validate current status
        if "current_status" in pattern_data:
            if pattern_data["current_status"] not in DashboardValidator.VALID_STATUSES:
                return False, f"Invalid status: {pattern_data['current_status']}"
        
        # Validate category breakdown if present
        if "category_breakdown" in pattern_data:
            if not isinstance(pattern_data["category_breakdown"], dict):
                return False, "category_breakdown must be a dictionary"
            
            for category, value in pattern_data["category_breakdown"].items():
                if not isinstance(category, str) or not category.strip():
                    return False, "category_breakdown keys must be non-empty strings"
                try:
                    val = float(value)
                    if val < 0:
                        return False, f"category_breakdown values cannot be negative: {category}"
                except (ValueError, TypeError):
                    return False, "category_breakdown values must be numeric"
        
        # Validate peak hours if present
        if "peak_hours" in pattern_data:
            if not isinstance(pattern_data["peak_hours"], list):
                return False, "peak_hours must be a list"
            
            for time_range in pattern_data["peak_hours"]:
                if not DashboardValidator._is_valid_time_range(time_range):
                    return False, f"Invalid time range: {time_range}"
        
        # Validate last activity timestamp if present
        if "last_activity" in pattern_data:
            if pattern_data["last_activity"] and not DashboardValidator._is_valid_iso_timestamp(pattern_data["last_activity"]):
                return False, "last_activity must be valid ISO timestamp"
        
        return True, None
    
    @staticmethod
    def validate_dashboard_snapshot(snapshot_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate complete dashboard snapshot.
        
        Args:
            snapshot_data: Dashboard snapshot data
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(snapshot_data, dict):
            return False, "Snapshot must be a dictionary"
        
        # Validate period
        if "period" in snapshot_data:
            if snapshot_data["period"] not in DashboardValidator.VALID_PERIODS:
                return False, f"Invalid period: {snapshot_data['period']}"
        
        # Validate team metrics
        if "team_metrics" in snapshot_data:
            if not isinstance(snapshot_data["team_metrics"], list):
                return False, "team_metrics must be a list"
            
            for metric in snapshot_data["team_metrics"]:
                is_valid, error = DashboardValidator.validate_team_metric(metric)
                if not is_valid:
                    return False, f"Invalid metric: {error}"
        
        # Validate employee patterns
        if "employee_patterns" in snapshot_data:
            if not isinstance(snapshot_data["employee_patterns"], dict):
                return False, "employee_patterns must be a dictionary"
            
            for emp_id, pattern in snapshot_data["employee_patterns"].items():
                if not isinstance(emp_id, str) or not emp_id.strip():
                    return False, "employee_id keys must be non-empty strings"
                
                is_valid, error = DashboardValidator.validate_employee_pattern(pattern)
                if not is_valid:
                    return False, f"Invalid pattern for {emp_id}: {error}"
        
        # Validate aggregates
        if "total_team_hours" in snapshot_data:
            try:
                hours = float(snapshot_data["total_team_hours"])
                if hours < 0:
                    return False, "total_team_hours cannot be negative"
            except (ValueError, TypeError):
                return False, "total_team_hours must be numeric"
        
        if "total_tasks_completed" in snapshot_data:
            try:
                tasks = int(snapshot_data["total_tasks_completed"])
                if tasks < 0:
                    return False, "total_tasks_completed cannot be negative"
            except (ValueError, TypeError):
                return False, "total_tasks_completed must be integer"
        
        if "team_average_productivity" in snapshot_data:
            try:
                avg = float(snapshot_data["team_average_productivity"])
                if not (0.0 <= avg <= 100.0):
                    return False, "team_average_productivity must be between 0 and 100"
            except (ValueError, TypeError):
                return False, "team_average_productivity must be numeric"
        
        # Validate period dates
        if "period_start" in snapshot_data and snapshot_data["period_start"]:
            if not DashboardValidator._is_valid_iso_timestamp(snapshot_data["period_start"]):
                return False, "period_start must be valid ISO timestamp"
        
        if "period_end" in snapshot_data and snapshot_data["period_end"]:
            if not DashboardValidator._is_valid_iso_timestamp(snapshot_data["period_end"]):
                return False, "period_end must be valid ISO timestamp"
        
        # Validate period_start <= period_end
        if "period_start" in snapshot_data and "period_end" in snapshot_data:
            if snapshot_data["period_start"] and snapshot_data["period_end"]:
                if snapshot_data["period_start"] > snapshot_data["period_end"]:
                    return False, "period_start must be <= period_end"
        
        # Validate timestamp
        if "timestamp" in snapshot_data:
            if not DashboardValidator._is_valid_iso_timestamp(snapshot_data["timestamp"]):
                return False, "Invalid snapshot timestamp"
        
        return True, None
    
    @staticmethod
    def validate_employee_data_input(employee_data: Dict[str, Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        """
        Validate input employee data for dashboard creation.
        
        Args:
            employee_data: Dict mapping employee_id to work data
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(employee_data, dict):
            return False, "employee_data must be a dictionary"
        
        if not employee_data:
            return False, "employee_data cannot be empty"
        
        for emp_id, data in employee_data.items():
            if not isinstance(emp_id, str) or not emp_id.strip():
                return False, "employee_id must be non-empty string"
            
            if not isinstance(data, dict):
                return False, f"Data for {emp_id} must be a dictionary"
            
            # Validate optional fields if present
            if "total_hours" in data:
                try:
                    hours = float(data["total_hours"])
                    if hours < 0:
                        return False, f"{emp_id}: total_hours cannot be negative"
                except (ValueError, TypeError):
                    return False, f"{emp_id}: total_hours must be numeric"
            
            if "tasks_completed" in data:
                try:
                    tasks = int(data["tasks_completed"])
                    if tasks < 0:
                        return False, f"{emp_id}: tasks_completed cannot be negative"
                except (ValueError, TypeError):
                    return False, f"{emp_id}: tasks_completed must be integer"
            
            if "productivity_score" in data:
                try:
                    score = float(data["productivity_score"])
                    if not (0.0 <= score <= 100.0):
                        return False, f"{emp_id}: productivity_score must be 0-100"
                except (ValueError, TypeError):
                    return False, f"{emp_id}: productivity_score must be numeric"
        
        return True, None
    
    @staticmethod
    def _is_valid_iso_timestamp(timestamp_str: str) -> bool:
        """Validate ISO 8601 timestamp format."""
        if not isinstance(timestamp_str, str):
            return False
        
        try:
            # Try parsing with timezone
            if "+" in timestamp_str or timestamp_str.endswith("Z"):
                # Remove timezone for parsing
                clean_ts = timestamp_str
                if "+" in clean_ts:
                    clean_ts = clean_ts.split("+")[0]
                elif clean_ts.endswith("Z"):
                    clean_ts = clean_ts[:-1]
                datetime.fromisoformat(clean_ts)
            else:
                datetime.fromisoformat(timestamp_str)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def _is_valid_time_range(time_range: str) -> bool:
        """Validate HH:MM-HH:MM format."""
        if not isinstance(time_range, str):
            return False
        
        if "-" not in time_range:
            return False
        
        try:
            start_str, end_str = time_range.split("-", 1)
            
            # Parse time strings
            start_parts = start_str.strip().split(":")
            end_parts = end_str.strip().split(":")
            
            if len(start_parts) != 2 or len(end_parts) != 2:
                return False
            
            start_hour = int(start_parts[0])
            start_min = int(start_parts[1])
            end_hour = int(end_parts[0])
            end_min = int(end_parts[1])
            
            # Validate ranges
            if not (0 <= start_hour < 24 and 0 <= start_min < 60):
                return False
            if not (0 <= end_hour < 24 and 0 <= end_min < 60):
                return False
            
            # Start should be before end
            start_minutes = start_hour * 60 + start_min
            end_minutes = end_hour * 60 + end_min
            if start_minutes >= end_minutes:
                return False
            
            return True
        except (ValueError, AttributeError):
            return False
