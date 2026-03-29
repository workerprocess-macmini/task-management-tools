"""
Unit Tests for Time Validators

Feature 1: Time Tracking & Duration
Tests: All validation functions
"""

import unittest
from datetime import datetime, timedelta
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from time_validators import (
    TimeValidationError,
    validate_iso8601_timestamp,
    validate_duration_seconds,
    validate_category,
    validate_priority,
    validate_employee_id,
    validate_project_name,
    validate_task_id,
    validate_notes,
    validate_pause_data,
)


class TestTimestampValidation(unittest.TestCase):
    """Test timestamp validation."""
    
    def test_valid_timestamp(self):
        """Test valid ISO 8601 timestamp."""
        ts, ts_utc = validate_iso8601_timestamp("2026-03-28T10:30:00+07:00")
        self.assertEqual(ts, "2026-03-28T10:30:00+07:00")
        self.assertIsNotNone(ts_utc)
    
    def test_missing_timezone(self):
        """Test timestamp without timezone."""
        with self.assertRaises(TimeValidationError):
            validate_iso8601_timestamp("2026-03-28T10:30:00")
    
    def test_invalid_format(self):
        """Test invalid timestamp format."""
        with self.assertRaises(TimeValidationError):
            validate_iso8601_timestamp("2026/03/28 10:30:00")
    
    def test_too_far_in_past(self):
        """Test timestamp too far in the past."""
        # 40 days ago
        past = (datetime.now() - timedelta(days=40)).isoformat()
        with self.assertRaises(TimeValidationError):
            validate_iso8601_timestamp(past + "+00:00")


class TestDurationValidation(unittest.TestCase):
    """Test duration validation."""
    
    def test_valid_duration(self):
        """Test valid durations."""
        dur, human = validate_duration_seconds(60)
        self.assertEqual(dur, 60)
        self.assertEqual(human, "1m")
        
        dur, human = validate_duration_seconds(3661)
        self.assertEqual(dur, 3661)
        self.assertEqual(human, "1h 1m 1s")
    
    def test_too_short(self):
        """Test duration less than 1 minute."""
        with self.assertRaises(TimeValidationError):
            validate_duration_seconds(30)
    
    def test_too_long(self):
        """Test duration more than 12 hours."""
        with self.assertRaises(TimeValidationError):
            validate_duration_seconds(43201)  # 12 hours + 1 second
    
    def test_invalid_type(self):
        """Test non-integer duration."""
        with self.assertRaises(TimeValidationError):
            validate_duration_seconds("not a number")


class TestCategoryValidation(unittest.TestCase):
    """Test category validation."""
    
    def test_valid_categories(self):
        """Test all valid categories."""
        valid = ["development", "testing", "devops", "management", "communication", "other"]
        
        for cat in valid:
            normalized, desc = validate_category(cat)
            self.assertEqual(normalized, cat)
            self.assertIsNotNone(desc)
    
    def test_case_insensitive(self):
        """Test case insensitivity."""
        normalized, _ = validate_category("DEVELOPMENT")
        self.assertEqual(normalized, "development")
        
        normalized, _ = validate_category("TeStInG")
        self.assertEqual(normalized, "testing")
    
    def test_invalid_category(self):
        """Test invalid category."""
        with self.assertRaises(TimeValidationError):
            validate_category("invalid_category")
    
    def test_empty_category(self):
        """Test empty category defaults to other."""
        # Empty string should fail, not default
        with self.assertRaises(TimeValidationError):
            validate_category("")


class TestPriorityValidation(unittest.TestCase):
    """Test priority validation."""
    
    def test_valid_priorities(self):
        """Test all valid priorities."""
        valid = [
            ("low", 1),
            ("medium", 2),
            ("high", 3),
            ("critical", 4)
        ]
        
        for pri, expected_weight in valid:
            normalized, weight, desc = validate_priority(pri)
            self.assertEqual(normalized, pri)
            self.assertEqual(weight, expected_weight)
            self.assertIsNotNone(desc)
    
    def test_case_insensitive(self):
        """Test case insensitivity."""
        normalized, _, _ = validate_priority("CRITICAL")
        self.assertEqual(normalized, "critical")
    
    def test_invalid_priority(self):
        """Test invalid priority."""
        with self.assertRaises(TimeValidationError):
            validate_priority("urgent")


class TestEmployeeIdValidation(unittest.TestCase):
    """Test employee ID validation."""
    
    def test_valid_employee_id(self):
        """Test valid employee IDs."""
        emp = validate_employee_id("emp001")
        self.assertEqual(emp, "emp001")
        
        emp = validate_employee_id("  emp002  ")
        self.assertEqual(emp, "emp002")
    
    def test_empty_employee_id(self):
        """Test empty employee ID."""
        with self.assertRaises(TimeValidationError):
            validate_employee_id("")
        
        with self.assertRaises(TimeValidationError):
            validate_employee_id("   ")
    
    def test_too_long_employee_id(self):
        """Test employee ID that's too long."""
        long_id = "x" * 101
        with self.assertRaises(TimeValidationError):
            validate_employee_id(long_id)


class TestProjectNameValidation(unittest.TestCase):
    """Test project name validation."""
    
    def test_valid_project_name(self):
        """Test valid project names."""
        proj = validate_project_name("PROJECT1")
        self.assertEqual(proj, "PROJECT1")
        
        proj = validate_project_name("  My Project  ")
        self.assertEqual(proj, "My Project")
    
    def test_empty_project_name(self):
        """Test empty project name."""
        with self.assertRaises(TimeValidationError):
            validate_project_name("")
    
    def test_too_long_project_name(self):
        """Test project name that's too long."""
        long_name = "x" * 101
        with self.assertRaises(TimeValidationError):
            validate_project_name(long_name)


class TestTaskIdValidation(unittest.TestCase):
    """Test task ID validation."""
    
    def test_valid_task_id(self):
        """Test valid task IDs."""
        task = validate_task_id("task-123")
        self.assertEqual(task, "task-123")
    
    def test_empty_task_id(self):
        """Test empty task ID."""
        with self.assertRaises(TimeValidationError):
            validate_task_id("")
    
    def test_too_long_task_id(self):
        """Test task ID that's too long."""
        long_id = "x" * 101
        with self.assertRaises(TimeValidationError):
            validate_task_id(long_id)


class TestNotesValidation(unittest.TestCase):
    """Test notes validation."""
    
    def test_valid_notes(self):
        """Test valid notes."""
        notes = validate_notes("Working on API endpoint")
        self.assertEqual(notes, "Working on API endpoint")
        
        notes = validate_notes("  Some notes  ")
        self.assertEqual(notes, "Some notes")
    
    def test_empty_notes(self):
        """Test empty notes (should be allowed)."""
        notes = validate_notes("")
        self.assertEqual(notes, "")
    
    def test_too_long_notes(self):
        """Test notes that are too long."""
        long_notes = "x" * 1001
        with self.assertRaises(TimeValidationError):
            validate_notes(long_notes)
    
    def test_custom_max_length(self):
        """Test custom max length."""
        long_notes = "x" * 101
        with self.assertRaises(TimeValidationError):
            validate_notes(long_notes, max_length=100)


class TestPauseDataValidation(unittest.TestCase):
    """Test pause data validation."""
    
    def test_valid_pause_data(self):
        """Test valid pause data."""
        data = validate_pause_data(
            pause_start="2026-03-28T10:30:00+07:00",
            pause_end="2026-03-28T10:40:00+07:00",
            duration_seconds=600
        )
        
        self.assertEqual(data["duration_seconds"], 600)
    
    def test_invalid_timestamps(self):
        """Test invalid pause timestamps."""
        with self.assertRaises(TimeValidationError):
            validate_pause_data(
                pause_start="invalid",
                pause_end="2026-03-28T10:40:00+07:00",
                duration_seconds=600
            )
    
    def test_negative_duration(self):
        """Test negative pause duration."""
        with self.assertRaises(TimeValidationError):
            validate_pause_data(
                pause_start="2026-03-28T10:30:00+07:00",
                pause_end="2026-03-28T10:40:00+07:00",
                duration_seconds=-100
            )
    
    def test_duration_mismatch(self):
        """Test when duration doesn't match timestamps."""
        with self.assertRaises(TimeValidationError):
            validate_pause_data(
                pause_start="2026-03-28T10:30:00+07:00",
                pause_end="2026-03-28T10:40:00+07:00",
                duration_seconds=1000  # Should be 600
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
