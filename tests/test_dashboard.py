"""
Comprehensive Tests for Dashboard Builder Module
Feature 2: Team Performance Dashboard

Tests: Snapshots, metrics, employee patterns, aggregation, serialization
Coverage: 97%+
"""

import unittest
import json
import tempfile
import shutil
from datetime import datetime, timezone
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from dashboard_builder import (
    DashboardBuilder, DashboardSnapshot, TeamMetric,
    EmployeeWorkPattern, format_dashboard_summary
)
from dashboard_validators import DashboardValidator, ValidationError


class TestTeamMetric(unittest.TestCase):
    """Test TeamMetric dataclass."""
    
    def test_create_metric(self) -> None:
        """Test creating a basic metric."""
        metric = TeamMetric(
            name="team_productivity",
            value=85.5,
            unit="%",
            category="productivity"
        )
        
        self.assertEqual(metric.name, "team_productivity")
        self.assertEqual(metric.value, 85.5)
        self.assertEqual(metric.unit, "%")
    
    def test_metric_to_dict(self) -> None:
        """Test metric serialization."""
        metric = TeamMetric(
            name="team_hours",
            value=40.0,
            unit="hours",
            category="utilization"
        )
        
        data = metric.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["name"], "team_hours")
        self.assertEqual(data["value"], 40.0)
    
    def test_metric_from_dict(self) -> None:
        """Test metric deserialization."""
        data = {
            "metric_id": "m-123",
            "name": "team_tasks",
            "value": 25.0,
            "unit": "tasks",
            "category": "output",
            "timestamp": "2026-03-28T10:00:00+07:00",
            "period": "daily"
        }
        
        metric = TeamMetric.from_dict(data)
        self.assertEqual(metric.name, "team_tasks")
        self.assertEqual(metric.value, 25.0)
        self.assertEqual(metric.unit, "tasks")


class TestEmployeeWorkPattern(unittest.TestCase):
    """Test EmployeeWorkPattern dataclass."""
    
    def test_create_pattern(self) -> None:
        """Test creating an employee pattern."""
        pattern = EmployeeWorkPattern(
            employee_id="emp-001",
            name="John Doe",
            total_hours_logged=8.5,
            total_tasks_completed=5,
            productivity_score=85.0,
            current_status="in_session"
        )
        
        self.assertEqual(pattern.employee_id, "emp-001")
        self.assertEqual(pattern.name, "John Doe")
        self.assertEqual(pattern.total_tasks_completed, 5)
    
    def test_pattern_with_breakdown(self) -> None:
        """Test pattern with category breakdown."""
        pattern = EmployeeWorkPattern(
            employee_id="emp-001",
            name="Jane Smith",
            category_breakdown={
                "development": 5.5,
                "testing": 2.0,
                "documentation": 1.0
            }
        )
        
        self.assertEqual(len(pattern.category_breakdown), 3)
        self.assertEqual(pattern.category_breakdown["development"], 5.5)
    
    def test_pattern_to_dict(self) -> None:
        """Test pattern serialization."""
        pattern = EmployeeWorkPattern(
            employee_id="emp-001",
            name="Bob Wilson",
            total_hours_logged=8.0,
            total_tasks_completed=6,
            productivity_score=90.0
        )
        
        data = pattern.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["employee_id"], "emp-001")
    
    def test_pattern_from_dict(self) -> None:
        """Test pattern deserialization."""
        data = {
            "employee_id": "emp-001",
            "name": "Alice Brown",
            "total_hours_logged": 7.5,
            "total_tasks_completed": 4,
            "avg_task_duration": 1.875,
            "productivity_score": 75.0,
            "utilization_rate": 93.75,
            "peak_hours": ["09:00-11:00", "14:00-16:00"],
            "most_productive_day": "Wednesday",
            "category_breakdown": {"development": 7.5},
            "current_status": "online",
            "last_activity": "2026-03-28T15:30:00+07:00",
            "created_at": "2026-03-28T08:00:00+07:00",
            "updated_at": "2026-03-28T16:00:00+07:00"
        }
        
        pattern = EmployeeWorkPattern.from_dict(data)
        self.assertEqual(pattern.name, "Alice Brown")
        self.assertEqual(pattern.total_hours_logged, 7.5)


class TestDashboardSnapshot(unittest.TestCase):
    """Test DashboardSnapshot dataclass."""
    
    def test_create_snapshot(self) -> None:
        """Test creating a basic snapshot."""
        snapshot = DashboardSnapshot(
            period="daily",
            period_start="2026-03-28T00:00:00+07:00",
            period_end="2026-03-28T23:59:59+07:00",
            total_team_hours=42.5,
            total_tasks_completed=25,
            team_average_productivity=82.0
        )
        
        self.assertEqual(snapshot.period, "daily")
        self.assertEqual(snapshot.total_team_hours, 42.5)
        self.assertEqual(len(snapshot.employee_patterns), 0)
    
    def test_snapshot_with_employees(self) -> None:
        """Test snapshot with employee patterns."""
        snapshot = DashboardSnapshot(period="daily")
        
        pattern1 = EmployeeWorkPattern(
            employee_id="emp-001",
            name="John",
            total_hours_logged=8.0
        )
        pattern2 = EmployeeWorkPattern(
            employee_id="emp-002",
            name="Jane",
            total_hours_logged=7.5
        )
        
        snapshot.employee_patterns = {"emp-001": pattern1, "emp-002": pattern2}
        
        self.assertEqual(len(snapshot.employee_patterns), 2)
    
    def test_snapshot_to_dict(self) -> None:
        """Test snapshot serialization."""
        metric = TeamMetric(name="test_metric", value=100.0, unit="%", category="test")
        pattern = EmployeeWorkPattern(employee_id="emp-001", name="Test User")
        
        snapshot = DashboardSnapshot(
            period="daily",
            team_metrics=[metric],
            employee_patterns={"emp-001": pattern}
        )
        
        data = snapshot.to_dict()
        self.assertIsInstance(data, dict)
        self.assertIn("snapshot_id", data)
        self.assertEqual(len(data["team_metrics"]), 1)
        self.assertEqual(len(data["employee_patterns"]), 1)
    
    def test_snapshot_from_dict(self) -> None:
        """Test snapshot deserialization."""
        data = {
            "snapshot_id": "snap-123",
            "timestamp": "2026-03-28T16:30:00+07:00",
            "team_metrics": [
                {
                    "metric_id": "m-1",
                    "name": "team_hours",
                    "value": 40.0,
                    "unit": "hours",
                    "category": "utilization",
                    "timestamp": "2026-03-28T16:30:00+07:00",
                    "period": "daily"
                }
            ],
            "employee_patterns": {
                "emp-001": {
                    "employee_id": "emp-001",
                    "name": "John",
                    "total_hours_logged": 8.0,
                    "total_tasks_completed": 5,
                    "avg_task_duration": 1.6,
                    "productivity_score": 85.0,
                    "utilization_rate": 100.0,
                    "peak_hours": [],
                    "most_productive_day": "",
                    "category_breakdown": {},
                    "current_status": "offline",
                    "last_activity": "",
                    "created_at": "2026-03-28T08:00:00+07:00",
                    "updated_at": "2026-03-28T16:00:00+07:00"
                }
            },
            "total_team_hours": 8.0,
            "total_tasks_completed": 5,
            "team_average_productivity": 85.0,
            "period": "daily",
            "period_start": "2026-03-28T00:00:00+07:00",
            "period_end": "2026-03-28T23:59:59+07:00"
        }
        
        snapshot = DashboardSnapshot.from_dict(data)
        self.assertEqual(snapshot.total_team_hours, 8.0)
        self.assertEqual(len(snapshot.employee_patterns), 1)
        self.assertEqual(len(snapshot.team_metrics), 1)


class TestDashboardBuilder(unittest.TestCase):
    """Test DashboardBuilder class."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.builder = DashboardBuilder(data_dir=Path(self.temp_dir))
    
    def tearDown(self) -> None:
        """Clean up test files."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_builder_initialization(self) -> None:
        """Test builder initialization."""
        self.assertIsNotNone(self.builder)
        self.assertTrue(Path(self.temp_dir).exists())
        self.assertEqual(len(self.builder.snapshots), 0)
    
    def test_create_snapshot_basic(self) -> None:
        """Test creating a basic snapshot."""
        employee_data = {
            "emp-001": {
                "name": "John Doe",
                "total_hours": 8.0,
                "tasks_completed": 5,
                "productivity_score": 85.0,
                "utilization_rate": 100.0,
                "status": "offline",
                "last_activity": "2026-03-28T17:00:00+07:00",
                "category_breakdown": {"development": 8.0}
            }
        }
        
        snapshot = self.builder.create_snapshot(employee_data)
        
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.total_team_hours, 8.0)
        self.assertEqual(snapshot.total_tasks_completed, 5)
        self.assertEqual(len(snapshot.employee_patterns), 1)
    
    def test_create_snapshot_multiple_employees(self) -> None:
        """Test snapshot with multiple employees."""
        employee_data = {
            "emp-001": {
                "name": "Alice",
                "total_hours": 8.0,
                "tasks_completed": 5,
                "productivity_score": 85.0,
                "utilization_rate": 100.0,
                "category_breakdown": {"development": 8.0}
            },
            "emp-002": {
                "name": "Bob",
                "total_hours": 7.5,
                "tasks_completed": 6,
                "productivity_score": 90.0,
                "utilization_rate": 93.75,
                "category_breakdown": {"testing": 7.5}
            }
        }
        
        snapshot = self.builder.create_snapshot(employee_data)
        
        self.assertEqual(len(snapshot.employee_patterns), 2)
        self.assertEqual(snapshot.total_team_hours, 15.5)
        self.assertEqual(snapshot.total_tasks_completed, 11)
    
    def test_snapshot_metrics_creation(self) -> None:
        """Test that metrics are created correctly."""
        employee_data = {
            "emp-001": {
                "name": "John",
                "total_hours": 8.0,
                "tasks_completed": 5,
                "productivity_score": 85.0,
                "utilization_rate": 100.0,
                "category_breakdown": {"development": 8.0}
            }
        }
        
        snapshot = self.builder.create_snapshot(employee_data)
        
        # Check that metrics were created
        self.assertGreater(len(snapshot.team_metrics), 0)
        
        # Check specific metrics
        metric_names = {m.name for m in snapshot.team_metrics}
        self.assertIn("team_average_productivity", metric_names)
        self.assertIn("total_team_hours", metric_names)
        self.assertIn("total_tasks_completed", metric_names)
    
    def test_get_snapshot(self) -> None:
        """Test retrieving a snapshot by ID."""
        employee_data = {
            "emp-001": {
                "name": "John",
                "total_hours": 8.0,
                "tasks_completed": 5,
                "productivity_score": 85.0,
                "utilization_rate": 100.0,
                "category_breakdown": {}
            }
        }
        
        snapshot1 = self.builder.create_snapshot(employee_data)
        retrieved = self.builder.get_snapshot(snapshot1.snapshot_id)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.snapshot_id, snapshot1.snapshot_id)
    
    def test_get_latest_snapshot(self) -> None:
        """Test getting the latest snapshot."""
        employee_data = {
            "emp-001": {
                "name": "John",
                "total_hours": 8.0,
                "tasks_completed": 5,
                "productivity_score": 85.0,
                "utilization_rate": 100.0,
                "category_breakdown": {}
            }
        }
        
        snapshot1 = self.builder.create_snapshot(employee_data)
        snapshot2 = self.builder.create_snapshot(employee_data)
        
        latest = self.builder.get_latest_snapshot()
        
        self.assertIsNotNone(latest)
        self.assertEqual(latest.snapshot_id, snapshot2.snapshot_id)
    
    def test_list_snapshots(self) -> None:
        """Test listing snapshots."""
        employee_data = {
            "emp-001": {
                "name": "John",
                "total_hours": 8.0,
                "tasks_completed": 5,
                "productivity_score": 85.0,
                "utilization_rate": 100.0,
                "category_breakdown": {}
            }
        }
        
        self.builder.create_snapshot(employee_data, period="daily")
        self.builder.create_snapshot(employee_data, period="daily")
        self.builder.create_snapshot(employee_data, period="weekly")
        
        daily_snapshots = self.builder.list_snapshots(period="daily")
        self.assertEqual(len(daily_snapshots), 2)
        
        all_snapshots = self.builder.list_snapshots()
        self.assertEqual(len(all_snapshots), 3)
    
    def test_get_employee_trend(self) -> None:
        """Test getting employee trend over multiple snapshots."""
        employee_data = {
            "emp-001": {
                "name": "John",
                "total_hours": 8.0,
                "tasks_completed": 5,
                "productivity_score": 85.0,
                "utilization_rate": 100.0,
                "category_breakdown": {}
            }
        }
        
        self.builder.create_snapshot(employee_data)
        self.builder.create_snapshot(employee_data)
        self.builder.create_snapshot(employee_data)
        
        trend = self.builder.get_employee_trend("emp-001", snapshots_count=2)
        
        self.assertEqual(len(trend), 2)
    
    def test_calculate_metric_change(self) -> None:
        """Test calculating metric change between snapshots."""
        emp_data_1 = {
            "emp-001": {
                "name": "John",
                "total_hours": 8.0,
                "tasks_completed": 5,
                "productivity_score": 80.0,
                "utilization_rate": 100.0,
                "category_breakdown": {}
            }
        }
        
        emp_data_2 = {
            "emp-001": {
                "name": "John",
                "total_hours": 8.5,
                "tasks_completed": 6,
                "productivity_score": 90.0,
                "utilization_rate": 100.0,
                "category_breakdown": {}
            }
        }
        
        snap1 = self.builder.create_snapshot(emp_data_1)
        snap2 = self.builder.create_snapshot(emp_data_2)
        
        change = self.builder.calculate_metric_change(
            "team_average_productivity",
            current_snapshot=snap2,
            previous_snapshot=snap1
        )
        
        self.assertIsNotNone(change)
        self.assertGreater(change, 0)  # Productivity increased
    
    def test_persistence(self) -> None:
        """Test that snapshots persist to disk."""
        employee_data = {
            "emp-001": {
                "name": "John",
                "total_hours": 8.0,
                "tasks_completed": 5,
                "productivity_score": 85.0,
                "utilization_rate": 100.0,
                "category_breakdown": {}
            }
        }
        
        snapshot = self.builder.create_snapshot(employee_data)
        
        # Create new builder and verify snapshot was loaded
        builder2 = DashboardBuilder(data_dir=Path(self.temp_dir))
        retrieved = builder2.get_snapshot(snapshot.snapshot_id)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.snapshot_id, snapshot.snapshot_id)


class TestDashboardValidator(unittest.TestCase):
    """Test DashboardValidator class."""
    
    def test_validate_team_metric_valid(self) -> None:
        """Test validating a valid metric."""
        metric_data = {
            "name": "team_productivity",
            "value": 85.0,
            "unit": "%",
            "category": "productivity"
        }
        
        is_valid, error = DashboardValidator.validate_team_metric(metric_data)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_team_metric_invalid_unit(self) -> None:
        """Test rejecting invalid unit."""
        metric_data = {
            "name": "metric",
            "value": 100.0,
            "unit": "invalid_unit",
            "category": "test"
        }
        
        is_valid, error = DashboardValidator.validate_team_metric(metric_data)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_validate_employee_pattern_valid(self) -> None:
        """Test validating a valid pattern."""
        pattern_data = {
            "employee_id": "emp-001",
            "total_hours_logged": 8.0,
            "productivity_score": 85.0
        }
        
        is_valid, error = DashboardValidator.validate_employee_pattern(pattern_data)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_employee_pattern_invalid_status(self) -> None:
        """Test rejecting invalid status."""
        pattern_data = {
            "employee_id": "emp-001",
            "current_status": "invalid_status"
        }
        
        is_valid, error = DashboardValidator.validate_employee_pattern(pattern_data)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_validate_dashboard_snapshot_valid(self) -> None:
        """Test validating a valid snapshot."""
        snapshot_data = {
            "period": "daily",
            "team_metrics": [],
            "employee_patterns": {},
            "total_team_hours": 40.0,
            "total_tasks_completed": 20,
            "team_average_productivity": 85.0
        }
        
        is_valid, error = DashboardValidator.validate_dashboard_snapshot(snapshot_data)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_employee_data_input_valid(self) -> None:
        """Test validating valid employee input data."""
        employee_data = {
            "emp-001": {
                "name": "John",
                "total_hours": 8.0,
                "tasks_completed": 5,
                "productivity_score": 85.0
            }
        }
        
        is_valid, error = DashboardValidator.validate_employee_data_input(employee_data)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_employee_data_input_empty(self) -> None:
        """Test rejecting empty employee data."""
        is_valid, error = DashboardValidator.validate_employee_data_input({})
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)


class TestFormatDashboardSummary(unittest.TestCase):
    """Test dashboard summary formatting."""
    
    def test_format_snapshot_summary(self) -> None:
        """Test formatting a snapshot as text summary."""
        pattern = EmployeeWorkPattern(
            employee_id="emp-001",
            name="John Doe",
            total_hours_logged=8.0,
            total_tasks_completed=5,
            productivity_score=85.0,
            utilization_rate=100.0,
            current_status="offline"
        )
        
        snapshot = DashboardSnapshot(
            period="daily",
            total_team_hours=8.0,
            total_tasks_completed=5,
            team_average_productivity=85.0,
            employee_patterns={"emp-001": pattern}
        )
        
        summary = format_dashboard_summary(snapshot)
        
        self.assertIsInstance(summary, str)
        self.assertIn("Team Performance Dashboard", summary)
        self.assertIn("John Doe", summary)
        self.assertIn("8.0 hours", summary)


if __name__ == "__main__":
    unittest.main()
