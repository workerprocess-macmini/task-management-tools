"""
Time Validation Module
Validates time-related data for the tracking system.

Feature 1: Time Tracking & Duration
"""

from __future__ import annotations

from datetime import datetime
from typing import Tuple


class TimeValidationError(ValueError):
    """Raised when time validation fails."""
    pass


def validate_iso8601_timestamp(timestamp: str) -> Tuple[str, str]:
    """
    Validate ISO 8601 timestamp with timezone.
    
    Args:
        timestamp: Timestamp string (e.g., "2026-03-28T10:30:00+07:00")
    
    Returns:
        Tuple of (original_timestamp, timestamp_in_utc)
    
    Raises:
        TimeValidationError: If timestamp is invalid
    """
    try:
        # Try parsing with timezone
        if "+" in timestamp or timestamp.endswith("Z"):
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        else:
            raise TimeValidationError(
                f"Timestamp must include timezone info (e.g., +07:00): {timestamp}"
            )
        
        # Verify it's a reasonable timestamp (not too far in past or future)
        now = datetime.now().astimezone()
        diff_hours = abs((dt - now).total_seconds() / 3600)
        
        if diff_hours > 730:  # More than 30 days
            raise TimeValidationError(
                f"Timestamp is suspiciously far from now (diff: {diff_hours} hours): {timestamp}"
            )
        
        return timestamp, dt.isoformat()
    
    except (ValueError, AttributeError) as e:
        raise TimeValidationError(
            f"Invalid ISO 8601 timestamp: {timestamp}. Error: {str(e)}"
        )


def validate_duration_seconds(seconds: int) -> Tuple[int, str]:
    """
    Validate duration in seconds.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Tuple of (duration_seconds, human_readable_string)
    
    Raises:
        TimeValidationError: If duration is invalid
    """
    try:
        seconds = int(seconds)
    except (ValueError, TypeError):
        raise TimeValidationError(f"Duration must be an integer (seconds): {seconds}")
    
    # Minimum 1 minute
    if seconds < 60:
        raise TimeValidationError(
            f"Duration must be at least 60 seconds (1 minute), got: {seconds}s"
        )
    
    # Maximum 12 hours per session
    if seconds > 43200:  # 12 * 3600
        raise TimeValidationError(
            f"Duration cannot exceed 43200 seconds (12 hours), got: {seconds}s"
        )
    
    # Format human-readable
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0:
        parts.append(f"{secs}s")
    
    human = " ".join(parts) if parts else "0s"
    return seconds, human


def validate_category(category: str) -> Tuple[str, str]:
    """
    Validate task category.
    
    Args:
        category: Category name
    
    Returns:
        Tuple of (normalized_category, description)
    
    Raises:
        TimeValidationError: If category is invalid
    """
    valid_categories = {
        "development": "Code writing, features, architecture",
        "testing": "QA, test writing, bug verification",
        "devops": "Infrastructure, deployment, monitoring",
        "management": "Planning, coordination, meetings",
        "communication": "Documentation, chat, support",
        "other": "Miscellaneous work",
    }
    
    normalized = (category or "").strip().lower()
    
    if normalized not in valid_categories:
        valid_list = ", ".join(valid_categories.keys())
        raise TimeValidationError(
            f"Invalid category: {category}. Valid: {valid_list}"
        )
    
    return normalized, valid_categories[normalized]


def validate_priority(priority: str) -> Tuple[str, int, str]:
    """
    Validate task priority.
    
    Args:
        priority: Priority name
    
    Returns:
        Tuple of (normalized_priority, weight, description)
    
    Raises:
        TimeValidationError: If priority is invalid
    """
    valid_priorities = {
        "low": (1, "Can be deferred, non-urgent"),
        "medium": (2, "Normal work, default"),
        "high": (3, "Should be completed soon"),
        "critical": (4, "Urgent, immediate attention"),
    }
    
    normalized = (priority or "").strip().lower()
    
    if normalized not in valid_priorities:
        valid_list = ", ".join(valid_priorities.keys())
        raise TimeValidationError(
            f"Invalid priority: {priority}. Valid: {valid_list}"
        )
    
    weight, description = valid_priorities[normalized]
    return normalized, weight, description


def validate_employee_id(employee_id: str) -> str:
    """
    Validate employee ID.
    
    Args:
        employee_id: Employee identifier
    
    Returns:
        Normalized employee ID
    
    Raises:
        TimeValidationError: If ID is invalid
    """
    normalized = (employee_id or "").strip()
    
    if not normalized:
        raise TimeValidationError("employee_id cannot be empty")
    
    if len(normalized) > 100:
        raise TimeValidationError(
            f"employee_id too long (max 100 chars): {len(normalized)}"
        )
    
    return normalized


def validate_project_name(project: str) -> str:
    """
    Validate project name.
    
    Args:
        project: Project name
    
    Returns:
        Normalized project name
    
    Raises:
        TimeValidationError: If name is invalid
    """
    normalized = (project or "").strip()
    
    if not normalized:
        raise TimeValidationError("project cannot be empty")
    
    if len(normalized) > 100:
        raise TimeValidationError(
            f"project name too long (max 100 chars): {len(normalized)}"
        )
    
    return normalized


def validate_task_id(task_id: str) -> str:
    """
    Validate task ID.
    
    Args:
        task_id: Task identifier
    
    Returns:
        Normalized task ID
    
    Raises:
        TimeValidationError: If ID is invalid
    """
    normalized = (task_id or "").strip()
    
    if not normalized:
        raise TimeValidationError("task_id cannot be empty")
    
    if len(normalized) > 100:
        raise TimeValidationError(
            f"task_id too long (max 100 chars): {len(normalized)}"
        )
    
    return normalized


def validate_notes(notes: str, max_length: int = 1000) -> str:
    """
    Validate session notes.
    
    Args:
        notes: Notes text
        max_length: Maximum allowed length
    
    Returns:
        Normalized notes
    
    Raises:
        TimeValidationError: If notes are invalid
    """
    normalized = (notes or "").strip()
    
    if len(normalized) > max_length:
        raise TimeValidationError(
            f"Notes too long (max {max_length} chars): {len(normalized)}"
        )
    
    return normalized


def validate_pause_data(
    pause_start: str,
    pause_end: str,
    duration_seconds: int
) -> dict:
    """
    Validate a pause period.
    
    Args:
        pause_start: Start timestamp (ISO 8601)
        pause_end: End timestamp (ISO 8601)
        duration_seconds: Duration in seconds
    
    Returns:
        Validated pause data dict
    
    Raises:
        TimeValidationError: If pause data is invalid
    """
    # Validate timestamps
    try:
        start = datetime.fromisoformat(pause_start.replace("Z", "+00:00"))
        end = datetime.fromisoformat(pause_end.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as e:
        raise TimeValidationError(f"Invalid pause timestamps: {e}")
    
    # Validate duration
    if duration_seconds < 0:
        raise TimeValidationError(f"Pause duration cannot be negative: {duration_seconds}")
    
    # Check consistency
    actual_duration = int((end - start).total_seconds())
    if actual_duration != duration_seconds:
        raise TimeValidationError(
            f"Pause duration mismatch: expected {actual_duration}s, got {duration_seconds}s"
        )
    
    return {
        "pause_start": pause_start,
        "pause_end": pause_end,
        "duration_seconds": duration_seconds,
    }


if __name__ == "__main__":
    # Demo validation
    try:
        print("Testing timestamp validation...")
        ts, ts_utc = validate_iso8601_timestamp("2026-03-28T10:30:00+07:00")
        print(f"✓ Valid: {ts}")
        
        print("\nTesting duration validation...")
        dur, human = validate_duration_seconds(7200)
        print(f"✓ Valid: {dur}s = {human}")
        
        print("\nTesting category validation...")
        cat, desc = validate_category("development")
        print(f"✓ Valid: {cat} ({desc})")
        
        print("\nTesting priority validation...")
        pri, weight, desc = validate_priority("high")
        print(f"✓ Valid: {pri} (weight: {weight}, {desc})")
        
        print("\nTesting invalid inputs...")
        try:
            validate_duration_seconds(30)  # Too short
        except TimeValidationError as e:
            print(f"✓ Caught error: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
