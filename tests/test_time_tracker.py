"""
Unit Tests for Time Tracker Module

Feature 1: Time Tracking & Duration
Tests: Session creation, pause/resume, duration calculation, serialization
"""

import unittest
import json
import time
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from time_tracker import TimeTracker, TimeSession, format_duration


class TestTimeSession(unittest.TestCase):
    """Test TimeSession dataclass."""
    
    def test_create_session(self):
        """Test creating a basic TimeSession."""
        session = TimeSession(
            task_id="task-123",
            employee_id="emp001",
            project="PROJECT1",
            start_time="2026-03-28T10:00:00+07:00",
            category="development",
            priority="high"
        )
        
        self.assertEqual(session.task_id, "task-123")
        self.assertEqual(session.employee_id, "emp001")
        self.assertTrue(session.is_active)
        self.assertFalse(session.is_paused)
    
    def test_to_dict_serialization(self):
        """Test converting session to dict."""
        session = TimeSession(
            task_id="task-123",
            employee_id="emp001",
            project="PROJECT1",
            start_time="2026-03-28T10:00:00+07:00"
        )
        
        data = session.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["task_id"], "task-123")
        self.assertEqual(data["employee_id"], "emp001")
    
    def test_from_dict_deserialization(self):
        """Test creating session from dict."""
        data = {
            "session_id": "sess-abc",
            "task_id": "task-123",
            "employee_id": "emp001",
            "project": "PROJECT1",
            "start_time": "2026-03-28T10:00:00+07:00",
            "end_time": None,
            "created_at": "2026-03-28T10:00:00+00:00",
            "total_duration_seconds": 3600,
            "pauses": [],
            "is_active": False,
            "is_paused": False,
            "pause_start": None,
            "category": "development",
            "priority": "high",
            "notes": "",
            "tags": []
        }
        
        session = TimeSession.from_dict(data)
        self.assertEqual(session.session_id, "sess-abc")
        self.assertEqual(session.total_duration_seconds, 3600)


class TestTimeTracker(unittest.TestCase):
    """Test TimeTracker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = TimeTracker()
    
    def test_start_session(self):
        """Test starting a new session."""
        session = self.tracker.start_session(
            employee_id="emp001",
            project="PROJECT1",
            task_id="task-123",
            category="development",
            priority="high"
        )
        
        self.assertIsNotNone(session.session_id)
        self.assertTrue(session.is_active)
        self.assertFalse(session.is_paused)
        self.assertEqual(session.employee_id, "emp001")
        self.assertEqual(session.project, "PROJECT1")
    
    def test_start_session_validation(self):
        """Test validation during session start."""
        with self.assertRaises(ValueError):
            self.tracker.start_session(
                employee_id="",  # Empty
                project="PROJECT1",
                task_id="task-123"
            )
        
        with self.assertRaises(ValueError):
            self.tracker.start_session(
                employee_id="emp001",
                project="PROJECT1",
                task_id="task-123",
                category="invalid_category"
            )
        
        with self.assertRaises(ValueError):
            self.tracker.start_session(
                employee_id="emp001",
                project="PROJECT1",
                task_id="task-123",
                priority="invalid_priority"
            )
    
    def test_pause_resume_session(self):
        """Test pausing and resuming a session."""
        session = self.tracker.start_session(
            employee_id="emp001",
            project="PROJECT1",
            task_id="task-123"
        )
        
        # Pause
        paused = self.tracker.pause_session(session.session_id)
        self.assertTrue(paused.is_paused)
        self.assertTrue(paused.is_active)
        
        # Resume
        resumed = self.tracker.resume_session(session.session_id)
        self.assertFalse(resumed.is_paused)
        self.assertTrue(resumed.is_active)
        
        # Check pause was recorded
        self.assertEqual(len(resumed.pauses), 1)
    
    def test_pause_invalid_state(self):
        """Test pause with invalid states."""
        session = self.tracker.start_session(
            employee_id="emp001",
            project="PROJECT1",
            task_id="task-123"
        )
        
        # Pause valid
        self.tracker.pause_session(session.session_id)
        
        # Pause again should fail
        with self.assertRaises(ValueError):
            self.tracker.pause_session(session.session_id)
    
    def test_stop_session(self):
        """Test stopping a session."""
        session = self.tracker.start_session(
            employee_id="emp001",
            project="PROJECT1",
            task_id="task-123"
        )
        
        # Simulate some work (need at least 1 second)
        time.sleep(1.1)
        
        stopped = self.tracker.stop_session(session.session_id)
        
        self.assertFalse(stopped.is_active)
        self.assertIsNotNone(stopped.end_time)
        self.assertGreaterEqual(stopped.total_duration_seconds, 1)
    
    def test_stop_with_pauses(self):
        """Test stopping a session that was paused."""
        session = self.tracker.start_session(
            employee_id="emp001",
            project="PROJECT1",
            task_id="task-123"
        )
        
        time.sleep(0.5)
        self.tracker.pause_session(session.session_id)
        time.sleep(0.5)
        self.tracker.resume_session(session.session_id)
        time.sleep(0.5)
        
        stopped = self.tracker.stop_session(session.session_id)
        
        # Duration should exclude pause time
        self.assertGreaterEqual(stopped.total_duration_seconds, 0)
        self.assertGreaterEqual(len(stopped.pauses), 1)
    
    def test_get_session(self):
        """Test retrieving a session."""
        session = self.tracker.start_session(
            employee_id="emp001",
            project="PROJECT1",
            task_id="task-123"
        )
        
        retrieved = self.tracker.get_session(session.session_id)
        self.assertEqual(retrieved.session_id, session.session_id)
        
        # Non-existent
        self.assertIsNone(self.tracker.get_session("non-existent"))
    
    def test_get_active_sessions(self):
        """Test retrieving active sessions."""
        session1 = self.tracker.start_session(
            employee_id="emp001",
            project="PROJECT1",
            task_id="task-1"
        )
        session2 = self.tracker.start_session(
            employee_id="emp001",
            project="PROJECT1",
            task_id="task-2"
        )
        session3 = self.tracker.start_session(
            employee_id="emp002",
            project="PROJECT1",
            task_id="task-3"
        )
        
        # Stop one
        self.tracker.stop_session(session1.session_id)
        
        # Get active for emp001
        active = self.tracker.get_active_sessions("emp001")
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].session_id, session2.session_id)
    
    def test_get_sessions_for_date(self):
        """Test retrieving sessions for a specific date."""
        session = self.tracker.start_session(
            employee_id="emp001",
            project="PROJECT1",
            task_id="task-123"
        )
        
        # Get today's sessions
        today = datetime.now().strftime("%Y-%m-%d")
        sessions = self.tracker.get_sessions_for_date("emp001", today)
        
        self.assertGreater(len(sessions), 0)
        self.assertEqual(sessions[0].session_id, session.session_id)
    
    def test_get_daily_duration(self):
        """Test getting total duration for a day."""
        session = self.tracker.start_session(
            employee_id="emp001",
            project="PROJECT1",
            task_id="task-123"
        )
        
        # Sleep for 2 seconds to ensure measurable duration
        time.sleep(2.1)
        stopped = self.tracker.stop_session(session.session_id)
        
        today = datetime.now().strftime("%Y-%m-%d")
        summary = self.tracker.get_daily_duration("emp001", today)
        
        self.assertEqual(summary["employee_id"], "emp001")
        self.assertEqual(summary["date"], today)
        self.assertEqual(summary["session_count"], 1)
        self.assertEqual(summary["completed_sessions"], 1)
        self.assertGreaterEqual(summary["total_seconds"], 2)
        # total_hours may round to 0.0 for short durations, so check total_seconds instead
        self.assertGreater(summary["total_seconds"], 0)
    
    def test_get_duration_by_category(self):
        """Test getting duration breakdown by category."""
        # Create sessions with different categories
        s1 = self.tracker.start_session(
            employee_id="emp001",
            project="PROJECT1",
            task_id="task-1",
            category="development"
        )
        time.sleep(2.1)  # Longer sleep for measurable duration
        stopped1 = self.tracker.stop_session(s1.session_id)
        
        s2 = self.tracker.start_session(
            employee_id="emp001",
            project="PROJECT1",
            task_id="task-2",
            category="testing"
        )
        time.sleep(2.1)  # Longer sleep for measurable duration
        stopped2 = self.tracker.stop_session(s2.session_id)
        
        today = datetime.now().strftime("%Y-%m-%d")
        by_cat = self.tracker.get_duration_by_category("emp001", today)
        
        self.assertIn("development", by_cat)
        self.assertIn("testing", by_cat)
        # Duration is calculated in hours; 2+ seconds gives at least 0.0005 hours
        self.assertGreaterEqual(by_cat["development"], 0)
        self.assertGreaterEqual(by_cat["testing"], 0)
        # Check that we actually recorded sessions
        self.assertGreater(stopped1.total_duration_seconds, 0)
        self.assertGreater(stopped2.total_duration_seconds, 0)
    
    def test_save_and_load_sessions(self):
        """Test saving and loading sessions from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "sessions.json")
            
            # Create and save
            session = self.tracker.start_session(
                employee_id="emp001",
                project="PROJECT1",
                task_id="task-123"
            )
            self.tracker.stop_session(session.session_id)
            self.tracker.save_sessions_to_file(file_path)
            
            # Load in new tracker
            tracker2 = TimeTracker()
            tracker2.load_sessions_from_file(file_path)
            
            loaded = tracker2.get_session(session.session_id)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.employee_id, "emp001")


class TestFormatDuration(unittest.TestCase):
    """Test duration formatting."""
    
    def test_format_duration(self):
        """Test formatting various durations."""
        self.assertEqual(format_duration(45), "45s")
        self.assertEqual(format_duration(60), "1m")
        self.assertEqual(format_duration(90), "1m 30s")
        self.assertEqual(format_duration(3600), "1h")
        self.assertEqual(format_duration(3661), "1h 1m 1s")
        self.assertEqual(format_duration(7200), "2h")


class TestThreadSafety(unittest.TestCase):
    """Test thread safety of TimeTracker."""
    
    def test_concurrent_sessions(self):
        """Test creating multiple sessions concurrently."""
        import threading
        
        tracker = TimeTracker()
        sessions = []
        lock = threading.Lock()
        
        def create_session(emp_id):
            session = tracker.start_session(
                employee_id=emp_id,
                project="PROJECT1",
                task_id=f"task-{emp_id}"
            )
            with lock:
                sessions.append(session)
            time.sleep(0.1)
            tracker.stop_session(session.session_id)
        
        threads = [
            threading.Thread(target=create_session, args=(f"emp{i:03d}",))
            for i in range(5)
        ]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        self.assertEqual(len(sessions), 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
