"""
Daily Summary Validators
Feature 3: Automated Daily Summary

Validates summary data, task data, and summary generation inputs.
Ensures data consistency and quality across summary operations.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class SummaryValidator:
    """Validates daily summary data and operations."""
    
    # Valid values
    VALID_STATUSES = {"generated", "sent", "delivered", "failed"}
    VALID_TASK_STATUSES = {"completed", "in_progress", "pending"}
    VALID_PRIORITIES = {"low", "medium", "high", "critical"}
    VALID_CATEGORIES = {"development", "testing", "devops", "documentation", "meetings", "other"}
    
    # Min/Max bounds
    MIN_HOURS = 0.0
    MAX_HOURS = 24.0
    MIN_TASKS = 0
    MAX_TASKS_PER_DAY = 50
    MIN_PRODUCTIVITY_SCORE = 0.0
    MAX_PRODUCTIVITY_SCORE = 100.0
    
    @staticmethod
    def validate_task_summary_item(task_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate task summary item.
        
        Args:
            task_data: Task data to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(task_data, dict):
            return False, "Task must be a dictionary"
        
        # Validate task_id
        if "task_id" in task_data:
            if not isinstance(task_data["task_id"], str):
                return False, "task_id must be string"
        
        # Validate title
        if "title" in task_data:
            if not isinstance(task_data["title"], str) or not task_data["title"].strip():
                return False, "title must be non-empty string"
        
        # Validate duration
        if "duration_hours" in task_data:
            try:
                hours = float(task_data["duration_hours"])
                if not (SummaryValidator.MIN_HOURS <= hours <= SummaryValidator.MAX_HOURS):
                    return False, f"duration_hours must be between {SummaryValidator.MIN_HOURS} and {SummaryValidator.MAX_HOURS}"
            except (ValueError, TypeError):
                return False, "duration_hours must be numeric"
        else:
            return False, "duration_hours is required"
        
        # Validate category
        if "category" in task_data:
            if task_data["category"] not in SummaryValidator.VALID_CATEGORIES:
                return False, f"Invalid category: {task_data['category']}"
        
        # Validate priority
        if "priority" in task_data:
            if task_data["priority"] not in SummaryValidator.VALID_PRIORITIES:
                return False, f"Invalid priority: {task_data['priority']}"
        
        # Validate status
        if "status" in task_data:
            if task_data["status"] not in SummaryValidator.VALID_TASK_STATUSES:
                return False, f"Invalid status: {task_data['status']}"
        
        # Validate completion_time if present
        if "completion_time" in task_data and task_data["completion_time"]:
            if not SummaryValidator._is_valid_iso_timestamp(task_data["completion_time"]):
                return False, "Invalid completion_time format"
        
        # Validate tags if present
        if "tags" in task_data:
            if not isinstance(task_data["tags"], list):
                return False, "tags must be a list"
            for tag in task_data["tags"]:
                if not isinstance(tag, str) or not tag.strip():
                    return False, "tags must contain non-empty strings"
        
        # Validate description if present
        if "description" in task_data:
            if not isinstance(task_data["description"], str):
                return False, "description must be string"
        
        # Validate notes if present
        if "notes" in task_data:
            if not isinstance(task_data["notes"], str):
                return False, "notes must be string"
        
        return True, None
    
    @staticmethod
    def validate_category_summary(category_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate category summary data.
        
        Args:
            category_data: Category summary data
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(category_data, dict):
            return False, "Category summary must be a dictionary"
        
        # Validate category
        if "category" not in category_data:
            return False, "Missing required field: category"
        
        if not isinstance(category_data["category"], str) or not category_data["category"].strip():
            return False, "category must be non-empty string"
        
        # Validate total_hours
        if "total_hours" in category_data:
            try:
                hours = float(category_data["total_hours"])
                if hours < 0:
                    return False, "total_hours cannot be negative"
            except (ValueError, TypeError):
                return False, "total_hours must be numeric"
        
        # Validate task_count
        if "task_count" in category_data:
            try:
                count = int(category_data["task_count"])
                if count < 0:
                    return False, "task_count cannot be negative"
            except (ValueError, TypeError):
                return False, "task_count must be integer"
        
        # Validate percentage_of_day
        if "percentage_of_day" in category_data:
            try:
                pct = float(category_data["percentage_of_day"])
                if not (0.0 <= pct <= 100.0):
                    return False, "percentage_of_day must be between 0 and 100"
            except (ValueError, TypeError):
                return False, "percentage_of_day must be numeric"
        
        return True, None
    
    @staticmethod
    def validate_daily_summary(summary_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate complete daily summary.
        
        Args:
            summary_data: Daily summary data
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(summary_data, dict):
            return False, "Summary must be a dictionary"
        
        # Validate employee_id
        if "employee_id" not in summary_data:
            return False, "Missing required field: employee_id"
        
        if not isinstance(summary_data["employee_id"], str) or not summary_data["employee_id"].strip():
            return False, "employee_id must be non-empty string"
        
        # Validate summary_date
        if "summary_date" not in summary_data:
            return False, "Missing required field: summary_date"
        
        if not SummaryValidator._is_valid_date(summary_data["summary_date"]):
            return False, f"Invalid summary_date format (expected YYYY-MM-DD): {summary_data['summary_date']}"
        
        # Validate employee_name
        if "employee_name" in summary_data:
            if not isinstance(summary_data["employee_name"], str):
                return False, "employee_name must be string"
        
        # Validate total_work_hours
        if "total_work_hours" in summary_data:
            try:
                hours = float(summary_data["total_work_hours"])
                if not (SummaryValidator.MIN_HOURS <= hours <= SummaryValidator.MAX_HOURS):
                    return False, f"total_work_hours must be between {SummaryValidator.MIN_HOURS} and {SummaryValidator.MAX_HOURS}"
            except (ValueError, TypeError):
                return False, "total_work_hours must be numeric"
        
        # Validate task counts
        if "total_tasks_completed" in summary_data:
            try:
                count = int(summary_data["total_tasks_completed"])
                if not (SummaryValidator.MIN_TASKS <= count <= SummaryValidator.MAX_TASKS_PER_DAY):
                    return False, f"total_tasks_completed must be between {SummaryValidator.MIN_TASKS} and {SummaryValidator.MAX_TASKS_PER_DAY}"
            except (ValueError, TypeError):
                return False, "total_tasks_completed must be integer"
        
        if "total_tasks_in_progress" in summary_data:
            try:
                count = int(summary_data["total_tasks_in_progress"])
                if not (SummaryValidator.MIN_TASKS <= count <= SummaryValidator.MAX_TASKS_PER_DAY):
                    return False, f"total_tasks_in_progress must be between {SummaryValidator.MIN_TASKS} and {SummaryValidator.MAX_TASKS_PER_DAY}"
            except (ValueError, TypeError):
                return False, "total_tasks_in_progress must be integer"
        
        # Validate productivity_score
        if "productivity_score" in summary_data:
            try:
                score = float(summary_data["productivity_score"])
                if not (SummaryValidator.MIN_PRODUCTIVITY_SCORE <= score <= SummaryValidator.MAX_PRODUCTIVITY_SCORE):
                    return False, f"productivity_score must be between {SummaryValidator.MIN_PRODUCTIVITY_SCORE} and {SummaryValidator.MAX_PRODUCTIVITY_SCORE}"
            except (ValueError, TypeError):
                return False, "productivity_score must be numeric"
        
        # Validate tasks
        if "tasks" in summary_data:
            if not isinstance(summary_data["tasks"], list):
                return False, "tasks must be a list"
            
            for task in summary_data["tasks"]:
                is_valid, error = SummaryValidator.validate_task_summary_item(task)
                if not is_valid:
                    return False, f"Invalid task: {error}"
        
        # Validate category_summaries
        if "category_summaries" in summary_data:
            if not isinstance(summary_data["category_summaries"], dict):
                return False, "category_summaries must be a dictionary"
            
            for category, cat_summary in summary_data["category_summaries"].items():
                if not isinstance(category, str) or not category.strip():
                    return False, "category_summaries keys must be non-empty strings"
                
                is_valid, error = SummaryValidator.validate_category_summary(cat_summary)
                if not is_valid:
                    return False, f"Invalid category summary for {category}: {error}"
        
        # Validate longest_task if present
        if "longest_task" in summary_data and summary_data["longest_task"]:
            is_valid, error = SummaryValidator.validate_task_summary_item(summary_data["longest_task"])
            if not is_valid:
                return False, f"Invalid longest_task: {error}"
        
        # Validate achievements
        if "top_achievements" in summary_data:
            if not isinstance(summary_data["top_achievements"], list):
                return False, "top_achievements must be a list"
            
            for achievement in summary_data["top_achievements"]:
                if not isinstance(achievement, str) or not achievement.strip():
                    return False, "top_achievements must contain non-empty strings"
        
        # Validate recommendations
        if "recommendations" in summary_data:
            if not isinstance(summary_data["recommendations"], list):
                return False, "recommendations must be a list"
            
            for rec in summary_data["recommendations"]:
                if not isinstance(rec, str) or not rec.strip():
                    return False, "recommendations must contain non-empty strings"
        
        # Validate status
        if "status" in summary_data:
            if summary_data["status"] not in SummaryValidator.VALID_STATUSES:
                return False, f"Invalid status: {summary_data['status']}"
        
        # Validate most_productive_hour if present
        if "most_productive_hour" in summary_data and summary_data["most_productive_hour"]:
            if not SummaryValidator._is_valid_hour_format(summary_data["most_productive_hour"]):
                return False, "Invalid most_productive_hour format (expected HH:00)"
        
        # Validate sent_at if present
        if "sent_at" in summary_data and summary_data["sent_at"]:
            if not SummaryValidator._is_valid_iso_timestamp(summary_data["sent_at"]):
                return False, "Invalid sent_at timestamp"
        
        # Validate generated_at
        if "generated_at" in summary_data:
            if not SummaryValidator._is_valid_iso_timestamp(summary_data["generated_at"]):
                return False, "Invalid generated_at timestamp"
        
        return True, None
    
    @staticmethod
    def validate_summary_generation_input(
        employee_id: str,
        employee_name: str,
        summary_date: str,
        tasks: List[Dict[str, Any]]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate input parameters for summary generation.
        
        Args:
            employee_id: Employee ID
            employee_name: Employee name
            summary_date: Summary date (YYYY-MM-DD)
            tasks: List of task data
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate employee_id
        if not isinstance(employee_id, str) or not employee_id.strip():
            return False, "employee_id must be non-empty string"
        
        # Validate employee_name
        if not isinstance(employee_name, str) or not employee_name.strip():
            return False, "employee_name must be non-empty string"
        
        # Validate summary_date
        if not SummaryValidator._is_valid_date(summary_date):
            return False, f"Invalid summary_date format (expected YYYY-MM-DD): {summary_date}"
        
        # Validate tasks
        if not isinstance(tasks, list):
            return False, "tasks must be a list"
        
        if not tasks:
            return False, "tasks list cannot be empty"
        
        if len(tasks) > SummaryValidator.MAX_TASKS_PER_DAY:
            return False, f"Too many tasks ({len(tasks)}, max {SummaryValidator.MAX_TASKS_PER_DAY})"
        
        for i, task in enumerate(tasks):
            is_valid, error = SummaryValidator.validate_task_summary_item(task)
            if not is_valid:
                return False, f"Invalid task at index {i}: {error}"
        
        return True, None
    
    @staticmethod
    def _is_valid_date(date_str: str) -> bool:
        """Validate YYYY-MM-DD date format."""
        if not isinstance(date_str, str):
            return False
        
        try:
            parts = date_str.split("-")
            if len(parts) != 3:
                return False
            
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            
            if not (1900 <= year <= 2100):
                return False
            if not (1 <= month <= 12):
                return False
            if not (1 <= day <= 31):
                return False
            
            # Additional check: valid day for month
            datetime(year, month, day)
            return True
        except (ValueError, AttributeError):
            return False
    
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
    def _is_valid_hour_format(hour_str: str) -> bool:
        """Validate HH:00 format."""
        if not isinstance(hour_str, str):
            return False
        
        try:
            if not hour_str.endswith(":00"):
                return False
            
            hour = int(hour_str.split(":")[0])
            if not (0 <= hour < 24):
                return False
            
            return True
        except (ValueError, AttributeError):
            return False
