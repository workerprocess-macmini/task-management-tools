"""
Insights Validators Module for Work Logging System
Validates productivity insights and related data.

Feature 4: Productivity Insights - Data Validation
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
import json


class InsightValidationError(Exception):
    """Exception raised for invalid insight data."""
    pass


def validate_employee_id(employee_id: str) -> bool:
    """
    Validate employee ID format.
    
    Args:
        employee_id: The employee ID to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        InsightValidationError: If validation fails
    """
    if not employee_id or not isinstance(employee_id, str):
        raise InsightValidationError("employee_id must be a non-empty string")
    if len(employee_id) > 100:
        raise InsightValidationError("employee_id exceeds maximum length of 100")
    if not employee_id.replace("-", "").replace("_", "").isalnum():
        raise InsightValidationError("employee_id contains invalid characters")
    return True


def validate_metric_name(metric_name: str) -> bool:
    """
    Validate metric name.
    
    Args:
        metric_name: The metric name to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        InsightValidationError: If validation fails
    """
    valid_metrics = {
        "tasks_per_hour", "tasks_per_day", "avg_task_duration",
        "focus_score", "balance_score", "consistency_score",
        "peak_hours", "productive_hours", "break_frequency",
        "category_distribution", "priority_distribution",
        "completion_rate", "context_switches", "deep_work_hours"
    }
    
    if not metric_name or metric_name not in valid_metrics:
        raise InsightValidationError(
            f"Invalid metric name: {metric_name}. Valid metrics: {', '.join(sorted(valid_metrics))}"
        )
    return True


def validate_metric_value(value: float, metric_name: Optional[str] = None) -> bool:
    """
    Validate metric value.
    
    Args:
        value: The metric value
        metric_name: Optional metric name for context-specific validation
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        InsightValidationError: If validation fails
    """
    if not isinstance(value, (int, float)):
        raise InsightValidationError(f"Metric value must be numeric, got {type(value)}")
    
    if value < 0:
        raise InsightValidationError("Metric value cannot be negative")
    
    # Context-specific validation
    if metric_name == "focus_score" and not (0 <= value <= 100):
        raise InsightValidationError("focus_score must be between 0 and 100")
    if metric_name == "balance_score" and not (0 <= value <= 100):
        raise InsightValidationError("balance_score must be between 0 and 100")
    if metric_name == "consistency_score" and not (0 <= value <= 100):
        raise InsightValidationError("consistency_score must be between 0 and 100")
    
    return True


def validate_pattern_type(pattern_type: str) -> bool:
    """
    Validate work pattern type.
    
    Args:
        pattern_type: The pattern type to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        InsightValidationError: If validation fails
    """
    valid_types = {
        "peak_hours", "low_hours", "category_focus", "break_pattern",
        "context_switching", "focus_blocks", "workload_trend",
        "consistency_pattern", "weekend_work", "overtime_pattern"
    }
    
    if not pattern_type or pattern_type not in valid_types:
        raise InsightValidationError(
            f"Invalid pattern type: {pattern_type}. Valid types: {', '.join(sorted(valid_types))}"
        )
    return True


def validate_insight_type(insight_type: str) -> bool:
    """
    Validate insight type.
    
    Args:
        insight_type: The insight type to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        InsightValidationError: If validation fails
    """
    valid_types = {"strength", "weakness", "opportunity", "pattern", "trend"}
    
    if not insight_type or insight_type not in valid_types:
        raise InsightValidationError(
            f"Invalid insight type: {insight_type}. Valid types: {', '.join(sorted(valid_types))}"
        )
    return True


def validate_severity(severity: str) -> bool:
    """
    Validate severity level.
    
    Args:
        severity: The severity level to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        InsightValidationError: If validation fails
    """
    valid_levels = {"info", "low", "medium", "high", "critical"}
    
    if not severity or severity not in valid_levels:
        raise InsightValidationError(
            f"Invalid severity: {severity}. Valid levels: {', '.join(sorted(valid_levels))}"
        )
    return True


def validate_confidence(confidence: float) -> bool:
    """
    Validate confidence score.
    
    Args:
        confidence: The confidence score (0.0 to 1.0)
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        InsightValidationError: If validation fails
    """
    if not isinstance(confidence, (int, float)):
        raise InsightValidationError(f"Confidence must be numeric, got {type(confidence)}")
    
    if not (0.0 <= confidence <= 1.0):
        raise InsightValidationError(f"Confidence must be between 0.0 and 1.0, got {confidence}")
    
    return True


def validate_date_string(date_str: str, allow_empty: bool = False) -> bool:
    """
    Validate date string format (YYYY-MM-DD).
    
    Args:
        date_str: The date string to validate
        allow_empty: If True, empty string is valid
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        InsightValidationError: If validation fails
    """
    if allow_empty and not date_str:
        return True
    
    if not date_str:
        raise InsightValidationError("Date string cannot be empty")
    
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        raise InsightValidationError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")


def validate_iso_timestamp(timestamp: str, allow_empty: bool = False) -> bool:
    """
    Validate ISO 8601 timestamp.
    
    Args:
        timestamp: The timestamp to validate
        allow_empty: If True, empty string is valid
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        InsightValidationError: If validation fails
    """
    if allow_empty and not timestamp:
        return True
    
    if not timestamp:
        raise InsightValidationError("Timestamp cannot be empty")
    
    try:
        # Check for space-based datetime format which is invalid for ISO 8601
        if " " in timestamp and "T" not in timestamp:
            raise InsightValidationError(f"Invalid ISO 8601 timestamp: {timestamp}")
        
        # Try parsing with timezone info
        if "+" in timestamp or timestamp.endswith("Z"):
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        else:
            datetime.fromisoformat(timestamp)
        return True
    except (ValueError, TypeError):
        raise InsightValidationError(f"Invalid ISO 8601 timestamp: {timestamp}")


def validate_period_type(period_type: str) -> bool:
    """
    Validate report period type.
    
    Args:
        period_type: The period type to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        InsightValidationError: If validation fails
    """
    valid_types = {"daily", "weekly", "monthly"}
    
    if not period_type or period_type not in valid_types:
        raise InsightValidationError(
            f"Invalid period type: {period_type}. Valid types: {', '.join(sorted(valid_types))}"
        )
    return True


def validate_action_category(category: str) -> bool:
    """
    Validate action category.
    
    Args:
        category: The category to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        InsightValidationError: If validation fails
    """
    valid_categories = {
        "time_management", "focus", "breaks", "workload", "schedule",
        "optimization", "improvement", "health"
    }
    
    if not category or category not in valid_categories:
        raise InsightValidationError(
            f"Invalid action category: {category}. Valid categories: {', '.join(sorted(valid_categories))}"
        )
    return True


def validate_impact_area(area: str) -> bool:
    """
    Validate impact area.
    
    Args:
        area: The impact area to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        InsightValidationError: If validation fails
    """
    valid_areas = {"Productivity", "Health", "Quality", "Efficiency"}
    
    if not area or area not in valid_areas:
        raise InsightValidationError(
            f"Invalid impact area: {area}. Valid areas: {', '.join(sorted(valid_areas))}"
        )
    return True


def validate_report_overall_score(score: float) -> bool:
    """
    Validate overall report score.
    
    Args:
        score: The score (0-100)
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        InsightValidationError: If validation fails
    """
    if not isinstance(score, (int, float)):
        raise InsightValidationError(f"Score must be numeric, got {type(score)}")
    
    if not (0 <= score <= 100):
        raise InsightValidationError(f"Score must be between 0 and 100, got {score}")
    
    return True


def validate_report_trend(trend: str) -> bool:
    """
    Validate report trend value.
    
    Args:
        trend: The trend value
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        InsightValidationError: If validation fails
    """
    valid_trends = {"improving", "stable", "declining"}
    
    if not trend or trend not in valid_trends:
        raise InsightValidationError(
            f"Invalid trend: {trend}. Valid trends: {', '.join(sorted(valid_trends))}"
        )
    return True


def validate_metric_data(metric_data: Dict[str, Any]) -> bool:
    """
    Validate a complete metric dictionary.
    
    Args:
        metric_data: The metric data to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        InsightValidationError: If validation fails
    """
    if not isinstance(metric_data, dict):
        raise InsightValidationError("Metric data must be a dictionary")
    
    # Required fields
    required = ["employee_id", "metric_name", "value", "measurement_date"]
    for field in required:
        if field not in metric_data:
            raise InsightValidationError(f"Missing required field: {field}")
    
    # Validate each field
    validate_employee_id(metric_data["employee_id"])
    validate_metric_name(metric_data["metric_name"])
    validate_metric_value(metric_data["value"], metric_data["metric_name"])
    validate_date_string(metric_data["measurement_date"])
    
    return True


def validate_insight_data(insight_data: Dict[str, Any]) -> bool:
    """
    Validate a complete insight dictionary.
    
    Args:
        insight_data: The insight data to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        InsightValidationError: If validation fails
    """
    if not isinstance(insight_data, dict):
        raise InsightValidationError("Insight data must be a dictionary")
    
    # Required fields
    required = ["employee_id", "title", "description", "insight_type", "confidence"]
    for field in required:
        if field not in insight_data:
            raise InsightValidationError(f"Missing required field: {field}")
    
    # Validate each field
    validate_employee_id(insight_data["employee_id"])
    
    if not insight_data.get("title"):
        raise InsightValidationError("title cannot be empty")
    
    if not insight_data.get("description"):
        raise InsightValidationError("description cannot be empty")
    
    validate_insight_type(insight_data["insight_type"])
    validate_confidence(insight_data["confidence"])
    
    # Optional fields
    if "severity" in insight_data:
        validate_severity(insight_data["severity"])
    
    if "action_category" in insight_data and insight_data["action_category"]:
        validate_action_category(insight_data["action_category"])
    
    if "impact_area" in insight_data and insight_data["impact_area"]:
        validate_impact_area(insight_data["impact_area"])
    
    return True


def validate_report_data(report_data: Dict[str, Any]) -> bool:
    """
    Validate a complete report dictionary.
    
    Args:
        report_data: The report data to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        InsightValidationError: If validation fails
    """
    if not isinstance(report_data, dict):
        raise InsightValidationError("Report data must be a dictionary")
    
    # Required fields
    required = ["employee_id", "period_start", "period_end", "overall_score"]
    for field in required:
        if field not in report_data:
            raise InsightValidationError(f"Missing required field: {field}")
    
    # Validate each field
    validate_employee_id(report_data["employee_id"])
    validate_date_string(report_data["period_start"])
    validate_date_string(report_data["period_end"])
    validate_report_overall_score(report_data["overall_score"])
    
    # Optional fields
    if "period_type" in report_data and report_data["period_type"]:
        validate_period_type(report_data["period_type"])
    
    if "trend" in report_data and report_data["trend"]:
        validate_report_trend(report_data["trend"])
    
    return True


def validate_json_schema(data: str) -> bool:
    """
    Validate that data is valid JSON.
    
    Args:
        data: The data to validate
        
    Returns:
        True if valid JSON, False otherwise
        
    Raises:
        InsightValidationError: If validation fails
    """
    try:
        json.loads(data)
        return True
    except json.JSONDecodeError as e:
        raise InsightValidationError(f"Invalid JSON: {str(e)}")
