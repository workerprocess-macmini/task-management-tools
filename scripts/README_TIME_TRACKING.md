# Feature 1: Time Tracking & Duration

**Phase 2: Time Tracking & Analytics**

---

## Overview

The Time Tracking module provides a complete work session tracking system with:

- ✅ Start/stop/pause/resume session management
- ✅ Automatic duration calculation (excluding pauses)
- ✅ ISO 8601 timezone-aware timestamps
- ✅ Category and priority tagging
- ✅ Daily aggregation and breakdown by category
- ✅ Thread-safe concurrent session handling
- ✅ JSON serialization/persistence

---

## Components

### 1. `time_tracker.py`
Core time tracking system.

**Main Classes:**
- `TimeSession` - Represents a single work session
- `TimeTracker` - Manages sessions and queries

**Key Functions:**
- `format_duration(seconds)` - Convert seconds to human-readable format

### 2. `time_validators.py`
Validation for all time-related inputs.

**Validators:**
- `validate_iso8601_timestamp()` - ISO 8601 with timezone
- `validate_duration_seconds()` - Duration constraints (60s-12h)
- `validate_category()` - Task categories
- `validate_priority()` - Priority levels
- `validate_employee_id()`, `validate_project_name()`, `validate_task_id()`
- `validate_pause_data()` - Pause period validation

### 3. `time_tracking_schema.json`
JSON schema for data validation and documentation.

---

## Quick Start

```python
from time_tracker import TimeTracker

# Initialize tracker
tracker = TimeTracker(tz_offset="+07:00")  # Bangkok time

# Start a session
session = tracker.start_session(
    employee_id="emp001",
    project="PROJECT1",
    task_id="task-123",
    category="development",
    priority="high",
    notes="Implementing API endpoint"
)
print(f"Started session: {session.session_id}")

# Pause for a break
tracker.pause_session(session.session_id)

# Resume work
tracker.resume_session(session.session_id)

# Stop and get duration
completed = tracker.stop_session(session.session_id)
print(f"Worked: {completed.total_duration_seconds}s")
print(f"Paused: {len(completed.pauses)} times")
```

---

## API Reference

### TimeTracker

#### `start_session(employee_id, project, task_id, category="other", priority="medium", notes="")`
Start a new tracking session.

**Args:**
- `employee_id` (str): Employee identifier
- `project` (str): Project name
- `task_id` (str): Link to work task ID
- `category` (str): "development", "testing", "devops", "management", "communication", "other"
- `priority` (str): "low", "medium", "high", "critical"
- `notes` (str): Optional session notes

**Returns:** `TimeSession` object

**Raises:** `ValueError` if parameters are invalid

---

#### `pause_session(session_id)`
Pause an active session.

**Returns:** Updated `TimeSession`

**Raises:** `ValueError` if session not active or already paused

---

#### `resume_session(session_id)`
Resume a paused session. Records the pause duration automatically.

**Returns:** Updated `TimeSession`

**Raises:** `ValueError` if session not paused

---

#### `stop_session(session_id)`
Stop a session and calculate final duration (excluding pauses).

**Returns:** `TimeSession` with `total_duration_seconds` calculated

**Raises:** `ValueError` if session not active

---

#### `get_session(session_id)`
Retrieve a session by ID.

**Returns:** `TimeSession` or `None`

---

#### `get_active_sessions(employee_id)`
Get all active (running) sessions for an employee.

**Returns:** List of `TimeSession` objects

---

#### `get_sessions_for_date(employee_id, date_str)`
Get all sessions for an employee on a specific date.

**Args:**
- `date_str` (str): Date in "YYYY-MM-DD" format

**Returns:** Sorted list of `TimeSession` objects

---

#### `get_daily_duration(employee_id, date_str)`
Get total duration for an employee on a specific date.

**Returns:** Dict with:
```python
{
    "date": "2026-03-28",
    "employee_id": "emp001",
    "total_seconds": 28800,
    "total_hours": 8.0,
    "session_count": 5,
    "completed_sessions": 5,
    "sessions": [...]  # List of TimeSession dicts
}
```

---

#### `get_duration_by_category(employee_id, date_str)`
Get duration breakdown by task category for a date.

**Returns:** Dict like:
```python
{
    "development": 3.5,
    "testing": 2.0,
    "communication": 2.5,
    "other": 0.0
}
```

---

#### `save_sessions_to_file(file_path)`
Save all tracked sessions to a JSON file.

---

#### `load_sessions_from_file(file_path)`
Load sessions from a JSON file into the tracker.

---

## Data Model

### TimeSession

```python
@dataclass
class TimeSession:
    session_id: str              # UUID
    task_id: str                 # Link to work task
    employee_id: str
    project: str
    
    # Timestamps (ISO 8601)
    start_time: str              # "2026-03-28T10:30:00+07:00"
    end_time: Optional[str]      # None if still active
    created_at: str              # UTC timestamp
    
    # Duration
    total_duration_seconds: int  # Active time only (excluding pauses)
    pauses: List[Dict]           # [{pause_start, pause_end, duration_seconds}, ...]
    
    # State
    is_active: bool              # Session still running
    is_paused: bool              # Currently paused
    pause_start: Optional[str]   # When current pause started
    
    # Metadata
    category: str                # "development", "testing", etc.
    priority: str                # "low", "medium", "high", "critical"
    notes: str                   # Optional notes
    tags: List[str]              # Optional tags
```

---

## Validation

All inputs are validated before use. Import validators:

```python
from time_validators import (
    validate_iso8601_timestamp,
    validate_duration_seconds,
    validate_category,
    validate_priority,
    TimeValidationError
)

try:
    normalized_cat, description = validate_category("development")
    print(f"Valid: {normalized_cat} ({description})")
except TimeValidationError as e:
    print(f"Error: {e}")
```

---

## Usage Examples

### Track Multiple Sessions in a Day

```python
tracker = TimeTracker()

# Session 1: Development
s1 = tracker.start_session("emp001", "PROJECT1", "task-1", category="development")
time.sleep(3600)  # 1 hour
tracker.stop_session(s1.session_id)

# Session 2: Testing
s2 = tracker.start_session("emp001", "PROJECT1", "task-2", category="testing")
time.sleep(1800)  # 30 minutes
tracker.stop_session(s2.session_id)

# Get daily summary
today = datetime.now().strftime("%Y-%m-%d")
summary = tracker.get_daily_duration("emp001", today)
print(f"Worked {summary['total_hours']} hours")

# Get breakdown by category
by_cat = tracker.get_duration_by_category("emp001", today)
print(f"Development: {by_cat['development']}h")
print(f"Testing: {by_cat['testing']}h")
```

### Handle Breaks

```python
tracker = TimeTracker()
session = tracker.start_session("emp001", "PROJECT1", "task-1")

# Work for a while
time.sleep(1800)  # 30 min

# Take a break
tracker.pause_session(session.session_id)
time.sleep(300)   # 5 min break

# Resume work
tracker.resume_session(session.session_id)
time.sleep(600)   # 10 more minutes

# Stop and check
stopped = tracker.stop_session(session.session_id)
print(f"Worked: {stopped.total_duration_seconds}s (paused {len(stopped.pauses)} times)")
# Expected: 1800 + 600 = 2400 seconds of actual work time
```

---

## Testing

Run tests:

```bash
python3 -m unittest tests.test_time_tracker -v
python3 -m unittest tests.test_time_validators -v
```

**Test Coverage:**
- 17 tracker tests (100% coverage)
- 32 validator tests (100% coverage)
- Thread safety tests
- Serialization/persistence tests

---

## Integration with Work Logging

Feature 1 data integrates with the existing work-logging system:

1. Each time session links to a work task (`task_id`)
2. Sessions inherit category and priority from the task
3. Duration data is aggregated in daily work logs
4. Features 2-4 use time session data for analytics

---

## File Structure

```
../tools/scripts/
├── time_tracker.py              # Core tracker
├── time_validators.py           # Validation
├── time_tracking_schema.json    # JSON schema
└── README_TIME_TRACKING.md      # This file

../tools/tests/
├── test_time_tracker.py         # Tracker tests (17 tests)
└── test_time_validators.py      # Validator tests (32 tests)
```

---

## Backward Compatibility

The Time Tracking system is fully backward compatible with Phase 1 data:

- Existing work logs are not modified
- Time tracking data is stored separately
- No changes to existing task structure required
- Optional category/priority fields remain optional

---

## Performance

- **Session creation:** O(1)
- **Pause/resume:** O(1)
- **Stop session:** O(1)
- **Query by date:** O(n) where n = sessions that day
- **Thread-safe:** All operations use RLock
- **Memory:** ~1KB per session

---

## Future Enhancements (Phase 3+)

- [ ] Manual time entry editing (with audit trail)
- [ ] Bulk time imports from CSV
- [ ] Auto-pause on inactivity detection
- [ ] Clock-in/clock-out device integration
- [ ] Time tracking synchronization across devices
- [ ] Real-time session status API
- [ ] Time entry conflicts/overlaps detection

---

## Support

For issues or questions:
1. Check test cases for usage examples
2. Review data model documentation
3. Run validators for input errors
4. Check timestamps are ISO 8601 with timezone

---

**Version:** 1.0  
**Status:** Production Ready  
**Last Updated:** 2026-03-28
