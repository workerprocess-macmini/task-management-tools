# Insights Generator Update - Phase 1 Log Format Support

## Summary
Updated `analyze_daily_logs()` function to work with Phase 1 log format that includes timestamp-based metrics instead of pre-calculated metric fields.

## Changes Made

### Updated Function: `analyze_daily_logs()`
**Location:** `/Users/chatmongkol/.openclaw/tools/scripts/insights_generators.py`

### Phase 1 Log Format (New)
The function now correctly parses logs in this format:
```json
{
  "task_id": "...",
  "timestamp": "2026-03-28 15:57:56",
  "timestamp_unix": 1774688276,
  "employee_id": "8557772399",
  "project": "Open Call",
  "status": "START",
  "current_status": "DONE",
  "subject": "งาน",
  "message": "...",
  "events": [
    {
      "timestamp": "2026-03-28 16:30:51",
      "timestamp_unix": 1774690251,
      "status": "DONE",
      "message": "เสร็จแล้ว"
    }
  ],
  "last_timestamp": "2026-03-28 16:30:51",
  "last_timestamp_unix": 1774690251
}
```

### Metrics Calculation Logic

#### 1. Duration Calculation
- **Formula:** `(last_timestamp_unix - timestamp_unix) / 60 = duration_minutes`
- **Example:** (1774690251 - 1774688276) / 60 = 32.92 minutes
- **Stored in:** `metrics["duration_minutes"]` and `metrics["total_hours"]`

#### 2. Interruptions Calculation
- **Method:** Count all events in the task
- **Formula:** `interruptions = len(events)` per task (summed across all tasks)
- **Meaning:** Each event (pause, resume, update, etc.) = 1 interruption
- **Stored in:** `metrics["interruptions"]`

#### 3. Context Switches Calculation
- **Formula:** `context_switches = max(0, num_tasks - 1)`
- **Logic:** Moving from one task to another = 1 context switch
- **Example:** 1 task = 0 switches; 2 tasks = 1 switch; 3 tasks = 2 switches
- **Stored in:** `metrics["context_switches"]`

#### 4. Deep Work Minutes Calculation
- **Formula:** `deep_work_hours = (total_duration_minutes * 0.8) / 60`
- **Logic:** 80% of total duration is "uninterrupted" deep work estimate
- **Rationale:** Reasonable estimate when we don't have explicit deep work tracking
- **Stored in:** `metrics["deep_work_hours"]`

#### 5. Task Count
- **Formula:** `task_count = len(tasks_array)`
- **Stored in:** `metrics["task_count"]`

### Return Structure
```python
{
    "interruptions": int,           # Total events across all tasks
    "context_switches": int,        # Task transitions (num_tasks - 1)
    "deep_work_hours": float,       # 80% of total duration
    "total_hours": float,           # Sum of all task durations
    "duration_minutes": float,      # Total duration in minutes
    "focus_score": float,           # 0-100 based on metrics
    "task_count": int,              # Number of tasks
    "categories": dict,             # Project distribution (%)
    "log_file": str,                # Path to log file
    "log_exists": bool              # Whether file was found
}
```

## Backward Compatibility

All three input modes remain fully functional:

### Mode 1: Auto-collect from logs (NEW - Primary)
```bash
python insights_generators.py --employee-id 8557772399 --date 2026-03-28
```
- Reads Phase 1 logs from `../../logs/{date}/{employee_id}.json`
- Calculates all metrics from timestamps
- Generates insights automatically

### Mode 2: Direct score input (UNCHANGED)
```bash
python insights_generators.py --employee-id 8557772399 --metrics 75
```
- Accepts pre-calculated focus score
- Still works exactly as before

### Mode 3: Raw metrics input (UNCHANGED)
```bash
python insights_generators.py --employee-id 8557772399 --interruptions 3 --context-switches 4 --deep-work-hours 5
```
- Accepts raw metric values
- Calculates focus score from metrics
- Still works exactly as before

## Testing Results

### Test 1: Single Task (Actual Log)
**Input:** `/logs/2026-03-28/8557772399.json` (1 task, 1 event)

**Calculated Metrics:**
- Duration: 32.92 minutes (1975 seconds)
- Interruptions: 1 (count of events)
- Context Switches: 0 (only 1 task)
- Deep Work Hours: 0.44 hours (80% of 32.92 min)
- Total Hours: 0.55 hours
- Task Count: 1
- Categories: Open Call 100%
- Focus Score: 100/100 ✅

### Test 2: Multiple Tasks
**Input:** 2 tasks with 3 total events

**Calculated Metrics:**
- Duration: 115 minutes (60 + 55)
- Interruptions: 3 (2 + 1 events)
- Context Switches: 1 (2 - 1)
- Deep Work Hours: 1.53 hours (80% of 115 min)
- Total Hours: 1.92 hours
- Task Count: 2
- Categories: Project A 50%, Project B 50%
- Focus Score: 100/100 ✅

### Test 3: Direct Metrics (Backward Compatibility)
**Input:** `--metrics 75`

**Output:** Focus Score 75/100 ✅

### Test 4: Raw Metrics (Backward Compatibility)
**Input:** `--interruptions 3 --context-switches 4 --deep-work-hours 5`

**Calculated:** Focus Score based on metrics ✅

## Key Implementation Details

1. **Unix Timestamp Parsing:** Uses `timestamp_unix` and `last_timestamp_unix` fields
2. **Event Counting:** Sums all events across all tasks as interruptions
3. **Multiple Tasks:** Properly handles multiple tasks with sum calculations
4. **Project Distribution:** Calculates percentage breakdown by project
5. **Error Handling:** Gracefully handles missing files and malformed data
6. **Path Resolution:** Uses relative path from script location: `../../logs`

## Files Modified

- `insights_generators.py` - Updated `analyze_daily_logs()` function
  - Replaced timestamp-based logic with Phase 1 format parsing
  - All metrics now calculated from available timestamp data
  - Maintains full backward compatibility

## Verification Checklist

✅ Reads Phase 1 log format correctly
✅ Calculates duration from timestamps
✅ Counts interruptions from events
✅ Calculates context switches from task count
✅ Estimates deep work as 80% of duration
✅ Sums metrics across multiple tasks
✅ Generates focus score correctly
✅ Returns proper data structure
✅ Backward compatible with all input modes
✅ Handles missing files gracefully
✅ Tested with single and multiple tasks
✅ JSON output works correctly

## Usage Examples

### Generate insights from logs (NEW - Recommended)
```bash
cd /Users/chatmongkol/.openclaw/tools/scripts
python insights_generators.py --employee-id 8557772399 --date 2026-03-28
```

### With JSON output for automation
```bash
python insights_generators.py --employee-id 8557772399 --date 2026-03-28 --output-json
```

### Programmatic usage in Python
```python
from insights_generators import analyze_daily_logs

metrics = analyze_daily_logs("8557772399", "2026-03-28")
print(f"Focus Score: {metrics['focus_score']}")
print(f"Total Hours: {metrics['total_hours']}")
print(f"Interruptions: {metrics['interruptions']}")
```

## Future Enhancements

- Current format uses 80% estimate for deep work - consider tracking explicit deep work periods in Phase 2
- Context switches could be enhanced with task type tracking
- Consider adding break detection in events
- Could implement pattern recognition for recurring task types
