"""
Comprehensive Tests for Daily Summary Generator
Feature 3: Automated Daily Summary

Tests: Summary generation, task processing, metrics, email formatting, persistence
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

from daily_summary import (
    DailySummaryGenerator, DailySummary, TaskSummaryItem,
    CategorySummary, format_summary_email
)
from summary_validators import SummaryValidator, ValidationError


class TestTaskSummaryItem(unittest.TestCase):
    """Test TaskSummaryItem dataclass."""
    
    def test_create_task(self) -> None:
        """Test creating a basic task item."""
        task = TaskSummaryItem(
            task_id="task-001",
            title="Fix login bug",
            duration_hours=2.5,
            category="development",
            priority="high",
            status="completed"
        )
        
        self.assertEqual(task.task_id, "task-001")
        self.assertEqual(task.title, "Fix login bug")
        self.assertEqual(task.duration_hours, 2.5)
    
    def test_task_with_tags(self) -> None:
        """Test task with tags."""
        task = TaskSummaryItem(
            task_id="task-001",
            title="API integration",
            duration_hours=3.0,
            tags=["backend", "critical", "urgent"]
        )
        
        self.assertEqual(len(task.tags), 3)
        self.assertIn("backend", task.tags)
    
    def test_task_to_dict(self) -> None:
        """Test task serialization."""
        task = TaskSummaryItem(
            task_id="task-001",
            title="Test",
            duration_hours=1.0,
            category="testing"
        )
        
        data = task.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["title"], "Test")
    
    def test_task_from_dict(self) -> None:
        """Test task deserialization."""
        data = {
            "task_id": "task-001",
            "title": "Refactor code",
            "duration_hours": 4.5,
            "category": "development",
            "priority": "medium",
            "status": "completed",
            "description": "Refactor auth module",
            "tags": ["refactoring", "cleanup"],
            "completion_time": "2026-03-28T15:30:00+07:00",
            "notes": "Completed on time"
        }
        
        task = TaskSummaryItem.from_dict(data)
        self.assertEqual(task.title, "Refactor code")
        self.assertEqual(task.duration_hours, 4.5)


class TestCategorySummary(unittest.TestCase):
    """Test CategorySummary dataclass."""
    
    def test_create_category_summary(self) -> None:
        """Test creating a category summary."""
        category = CategorySummary(
            category="development",
            total_hours=6.5,
            task_count=4,
            percentage_of_day=81.25
        )
        
        self.assertEqual(category.category, "development")
        self.assertEqual(category.total_hours, 6.5)
        self.assertEqual(category.task_count, 4)
    
    def test_category_to_dict(self) -> None:
        """Test category serialization."""
        category = CategorySummary(
            category="testing",
            total_hours=2.0,
            task_count=2,
            percentage_of_day=25.0
        )
        
        data = category.to_dict()
        self.assertEqual(data["category"], "testing")
        self.assertEqual(data["total_hours"], 2.0)
    
    def test_category_from_dict(self) -> None:
        """Test category deserialization."""
        data = {
            "category": "documentation",
            "total_hours": 1.5,
            "task_count": 1,
            "percentage_of_day": 18.75
        }
        
        category = CategorySummary.from_dict(data)
        self.assertEqual(category.category, "documentation")
        self.assertEqual(category.total_hours, 1.5)


class TestDailySummary(unittest.TestCase):
    """Test DailySummary dataclass."""
    
    def test_create_summary(self) -> None:
        """Test creating a basic summary."""
        summary = DailySummary(
            employee_id="emp-001",
            employee_name="John Doe",
            summary_date="2026-03-28"
        )
        
        self.assertEqual(summary.employee_id, "emp-001")
        self.assertEqual(summary.employee_name, "John Doe")
        self.assertEqual(summary.summary_date, "2026-03-28")
        self.assertEqual(summary.status, "generated")
    
    def test_summary_with_tasks(self) -> None:
        """Test summary with multiple tasks."""
        summary = DailySummary(
            employee_id="emp-001",
            employee_name="John",
            summary_date="2026-03-28"
        )
        
        task1 = TaskSummaryItem(
            task_id="t1",
            title="Task 1",
            duration_hours=2.0,
            status="completed"
        )
        task2 = TaskSummaryItem(
            task_id="t2",
            title="Task 2",
            duration_hours=3.0,
            status="completed"
        )
        
        summary.tasks = [task1, task2]
        
        self.assertEqual(len(summary.tasks), 2)
        self.assertEqual(summary.total_work_hours, 0.0)  # Not auto-calculated
    
    def test_summary_to_dict(self) -> None:
        """Test summary serialization."""
        summary = DailySummary(
            employee_id="emp-001",
            employee_name="John",
            summary_date="2026-03-28",
            total_work_hours=8.0,
            total_tasks_completed=5,
            productivity_score=85.0
        )
        
        data = summary.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["employee_id"], "emp-001")
        self.assertEqual(data["total_work_hours"], 8.0)
    
    def test_summary_from_dict(self) -> None:
        """Test summary deserialization."""
        data = {
            "summary_id": "sum-001",
            "employee_id": "emp-001",
            "employee_name": "Jane Smith",
            "summary_date": "2026-03-28",
            "generated_at": "2026-03-28T18:00:00+07:00",
            "total_work_hours": 8.5,
            "total_tasks_completed": 6,
            "total_tasks_in_progress": 0,
            "tasks": [],
            "category_summaries": {},
            "productivity_score": 88.0,
            "most_productive_hour": "10:00",
            "longest_task": None,
            "top_achievements": ["✅ Completed 6 tasks"],
            "observations": "Good day",
            "recommendations": [],
            "sent_at": None,
            "sent_to_email": None,
            "status": "generated"
        }
        
        summary = DailySummary.from_dict(data)
        self.assertEqual(summary.employee_id, "emp-001")
        self.assertEqual(summary.total_work_hours, 8.5)


class TestDailySummaryGenerator(unittest.TestCase):
    """Test DailySummaryGenerator class."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = DailySummaryGenerator(data_dir=Path(self.temp_dir))
    
    def tearDown(self) -> None:
        """Clean up test files."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generator_initialization(self) -> None:
        """Test generator initialization."""
        self.assertIsNotNone(self.generator)
        self.assertTrue(Path(self.temp_dir).exists())
        self.assertEqual(len(self.generator.summaries), 0)
    
    def test_generate_summary_basic(self) -> None:
        """Test generating a basic summary."""
        tasks = [
            {
                "task_id": "t1",
                "title": "Write documentation",
                "duration_hours": 2.0,
                "category": "documentation",
                "priority": "medium",
                "status": "completed"
            },
            {
                "task_id": "t2",
                "title": "Fix bugs",
                "duration_hours": 3.5,
                "category": "development",
                "priority": "high",
                "status": "completed"
            }
        ]
        
        summary = self.generator.generate_summary(
            employee_id="emp-001",
            employee_name="John Doe",
            summary_date="2026-03-28",
            tasks=tasks
        )
        
        self.assertIsNotNone(summary)
        self.assertEqual(summary.employee_id, "emp-001")
        self.assertEqual(summary.total_work_hours, 5.5)
        self.assertEqual(summary.total_tasks_completed, 2)
    
    def test_generate_summary_with_categories(self) -> None:
        """Test summary with category breakdown."""
        tasks = [
            {
                "task_id": "t1",
                "title": "Development task",
                "duration_hours": 5.0,
                "category": "development",
                "priority": "high",
                "status": "completed"
            },
            {
                "task_id": "t2",
                "title": "Test task",
                "duration_hours": 2.0,
                "category": "testing",
                "priority": "medium",
                "status": "completed"
            }
        ]
        
        summary = self.generator.generate_summary(
            employee_id="emp-001",
            employee_name="Jane",
            summary_date="2026-03-28",
            tasks=tasks
        )
        
        self.assertEqual(len(summary.category_summaries), 2)
        self.assertIn("development", summary.category_summaries)
        self.assertIn("testing", summary.category_summaries)
        
        # Check percentages
        dev_pct = summary.category_summaries["development"].percentage_of_day
        test_pct = summary.category_summaries["testing"].percentage_of_day
        self.assertAlmostEqual(dev_pct + test_pct, 100.0, places=1)
    
    def test_generate_summary_mixed_status(self) -> None:
        """Test summary with mixed task statuses."""
        tasks = [
            {
                "task_id": "t1",
                "title": "Completed",
                "duration_hours": 3.0,
                "category": "development",
                "status": "completed"
            },
            {
                "task_id": "t2",
                "title": "In progress",
                "duration_hours": 2.0,
                "category": "development",
                "status": "in_progress"
            }
        ]
        
        summary = self.generator.generate_summary(
            employee_id="emp-001",
            employee_name="Bob",
            summary_date="2026-03-28",
            tasks=tasks
        )
        
        self.assertEqual(summary.total_tasks_completed, 1)
        self.assertEqual(summary.total_tasks_in_progress, 1)
    
    def test_longest_task_tracking(self) -> None:
        """Test that longest task is tracked."""
        tasks = [
            {
                "task_id": "t1",
                "title": "Short task",
                "duration_hours": 1.0,
                "category": "documentation"
            },
            {
                "task_id": "t2",
                "title": "Long task",
                "duration_hours": 5.0,
                "category": "development"
            }
        ]
        
        summary = self.generator.generate_summary(
            employee_id="emp-001",
            employee_name="Test",
            summary_date="2026-03-28",
            tasks=tasks
        )
        
        self.assertIsNotNone(summary.longest_task)
        self.assertEqual(summary.longest_task.title, "Long task")
        self.assertEqual(summary.longest_task.duration_hours, 5.0)
    
    def test_productivity_score_calculation(self) -> None:
        """Test productivity score calculation."""
        # High productivity scenario
        tasks = [
            {
                "task_id": f"t{i}",
                "title": f"Task {i}",
                "duration_hours": 1.5,
                "category": "development",
                "status": "completed"
            }
            for i in range(6)
        ]
        
        summary = self.generator.generate_summary(
            employee_id="emp-001",
            employee_name="Productive",
            summary_date="2026-03-28",
            tasks=tasks
        )
        
        self.assertGreater(summary.productivity_score, 0.0)
        self.assertLessEqual(summary.productivity_score, 100.0)
    
    def test_achievements_generation(self) -> None:
        """Test that achievements are generated."""
        tasks = [
            {
                "task_id": f"t{i}",
                "title": f"Task {i}",
                "duration_hours": 1.5,
                "category": "development",
                "priority": "high",
                "status": "completed"
            }
            for i in range(6)
        ]
        
        summary = self.generator.generate_summary(
            employee_id="emp-001",
            employee_name="Achiever",
            summary_date="2026-03-28",
            tasks=tasks
        )
        
        self.assertGreater(len(summary.top_achievements), 0)
        self.assertIsInstance(summary.top_achievements[0], str)
    
    def test_recommendations_generation(self) -> None:
        """Test that recommendations are generated."""
        tasks = [
            {
                "task_id": "t1",
                "title": "Task 1",
                "duration_hours": 2.0,
                "category": "development",
                "status": "completed"
            }
        ]
        
        summary = self.generator.generate_summary(
            employee_id="emp-001",
            employee_name="Test",
            summary_date="2026-03-28",
            tasks=tasks
        )
        
        # Low hours should trigger recommendations
        if summary.total_work_hours < 6.0:
            self.assertGreater(len(summary.recommendations), 0)
    
    def test_get_summary(self) -> None:
        """Test retrieving a summary by ID."""
        tasks = [
            {
                "task_id": "t1",
                "title": "Task",
                "duration_hours": 1.0,
                "category": "development"
            }
        ]
        
        summary1 = self.generator.generate_summary(
            employee_id="emp-001",
            employee_name="John",
            summary_date="2026-03-28",
            tasks=tasks
        )
        
        retrieved = self.generator.get_summary(summary1.summary_id)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.summary_id, summary1.summary_id)
    
    def test_get_employee_summaries(self) -> None:
        """Test retrieving summaries for an employee."""
        tasks = [
            {
                "task_id": "t1",
                "title": "Task",
                "duration_hours": 1.0,
                "category": "development"
            }
        ]
        
        # Create multiple summaries for same employee
        for i in range(5):
            self.generator.generate_summary(
                employee_id="emp-001",
                employee_name="John",
                summary_date=f"2026-03-{20+i:02d}",
                tasks=tasks
            )
        
        summaries = self.generator.get_employee_summaries("emp-001", days=7)
        
        self.assertEqual(len(summaries), 5)
        self.assertTrue(all(s.employee_id == "emp-001" for s in summaries))
    
    def test_list_summaries(self) -> None:
        """Test listing all summaries."""
        tasks = [
            {
                "task_id": "t1",
                "title": "Task",
                "duration_hours": 1.0,
                "category": "development"
            }
        ]
        
        self.generator.generate_summary(
            employee_id="emp-001",
            employee_name="John",
            summary_date="2026-03-28",
            tasks=tasks
        )
        self.generator.generate_summary(
            employee_id="emp-002",
            employee_name="Jane",
            summary_date="2026-03-28",
            tasks=tasks
        )
        
        all_summaries = self.generator.list_summaries()
        
        self.assertEqual(len(all_summaries), 2)
    
    def test_list_summaries_by_date(self) -> None:
        """Test filtering summaries by date."""
        tasks = [
            {
                "task_id": "t1",
                "title": "Task",
                "duration_hours": 1.0,
                "category": "development"
            }
        ]
        
        self.generator.generate_summary(
            employee_id="emp-001",
            employee_name="John",
            summary_date="2026-03-28",
            tasks=tasks
        )
        self.generator.generate_summary(
            employee_id="emp-001",
            employee_name="John",
            summary_date="2026-03-29",
            tasks=tasks
        )
        
        march_28 = self.generator.list_summaries(summary_date="2026-03-28")
        self.assertEqual(len(march_28), 1)
    
    def test_mark_summary_sent(self) -> None:
        """Test marking a summary as sent."""
        tasks = [
            {
                "task_id": "t1",
                "title": "Task",
                "duration_hours": 1.0,
                "category": "development"
            }
        ]
        
        summary = self.generator.generate_summary(
            employee_id="emp-001",
            employee_name="John",
            summary_date="2026-03-28",
            tasks=tasks
        )
        
        success = self.generator.mark_summary_sent(
            summary.summary_id,
            email="john@example.com"
        )
        
        self.assertTrue(success)
        
        updated = self.generator.get_summary(summary.summary_id)
        self.assertEqual(updated.status, "sent")
        self.assertEqual(updated.sent_to_email, "john@example.com")
    
    def test_mark_summary_delivered(self) -> None:
        """Test marking a summary as delivered."""
        tasks = [
            {
                "task_id": "t1",
                "title": "Task",
                "duration_hours": 1.0,
                "category": "development"
            }
        ]
        
        summary = self.generator.generate_summary(
            employee_id="emp-001",
            employee_name="John",
            summary_date="2026-03-28",
            tasks=tasks
        )
        
        self.generator.mark_summary_sent(summary.summary_id)
        success = self.generator.mark_summary_delivered(summary.summary_id)
        
        self.assertTrue(success)
        
        updated = self.generator.get_summary(summary.summary_id)
        self.assertEqual(updated.status, "delivered")
    
    def test_persistence(self) -> None:
        """Test that summaries persist to disk."""
        tasks = [
            {
                "task_id": "t1",
                "title": "Task",
                "duration_hours": 1.0,
                "category": "development"
            }
        ]
        
        summary = self.generator.generate_summary(
            employee_id="emp-001",
            employee_name="John",
            summary_date="2026-03-28",
            tasks=tasks
        )
        
        # Create new generator and verify summary was loaded
        generator2 = DailySummaryGenerator(data_dir=Path(self.temp_dir))
        retrieved = generator2.get_summary(summary.summary_id)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.summary_id, summary.summary_id)


class TestSummaryValidator(unittest.TestCase):
    """Test SummaryValidator class."""
    
    def test_validate_task_item_valid(self) -> None:
        """Test validating a valid task."""
        task_data = {
            "task_id": "t1",
            "title": "Task",
            "duration_hours": 2.0,
            "category": "development",
            "priority": "high",
            "status": "completed"
        }
        
        is_valid, error = SummaryValidator.validate_task_summary_item(task_data)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_task_item_invalid_duration(self) -> None:
        """Test rejecting invalid duration."""
        task_data = {
            "task_id": "t1",
            "title": "Task",
            "duration_hours": 25.0,  # > 24 hours
            "category": "development"
        }
        
        is_valid, error = SummaryValidator.validate_task_summary_item(task_data)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_validate_category_summary_valid(self) -> None:
        """Test validating a valid category summary."""
        category_data = {
            "category": "development",
            "total_hours": 5.0,
            "task_count": 3,
            "percentage_of_day": 62.5
        }
        
        is_valid, error = SummaryValidator.validate_category_summary(category_data)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_daily_summary_valid(self) -> None:
        """Test validating a valid daily summary."""
        summary_data = {
            "employee_id": "emp-001",
            "employee_name": "John",
            "summary_date": "2026-03-28",
            "total_work_hours": 8.0,
            "total_tasks_completed": 5,
            "productivity_score": 85.0
        }
        
        is_valid, error = SummaryValidator.validate_daily_summary(summary_data)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_summary_generation_input_valid(self) -> None:
        """Test validating valid generation input."""
        tasks = [
            {
                "task_id": "t1",
                "title": "Task",
                "duration_hours": 1.0,
                "category": "development"
            }
        ]
        
        is_valid, error = SummaryValidator.validate_summary_generation_input(
            employee_id="emp-001",
            employee_name="John",
            summary_date="2026-03-28",
            tasks=tasks
        )
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_summary_generation_input_invalid_date(self) -> None:
        """Test rejecting invalid date."""
        tasks = [
            {"task_id": "t1", "title": "Task", "duration_hours": 1.0}
        ]
        
        is_valid, error = SummaryValidator.validate_summary_generation_input(
            employee_id="emp-001",
            employee_name="John",
            summary_date="03-28-2026",  # Wrong format
            tasks=tasks
        )
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)


class TestFormatSummaryEmail(unittest.TestCase):
    """Test summary email formatting."""
    
    def test_format_summary_email(self) -> None:
        """Test formatting summary as email."""
        summary = DailySummary(
            employee_id="emp-001",
            employee_name="John Doe",
            summary_date="2026-03-28",
            total_work_hours=8.0,
            total_tasks_completed=5,
            productivity_score=85.0,
            most_productive_hour="10:00",
            observations="Great day!",
            recommendations=["Take breaks"]
        )
        
        email_text = format_summary_email(summary)
        
        self.assertIsInstance(email_text, str)
        self.assertIn("John Doe", email_text)
        self.assertIn("2026-03-28", email_text)
        self.assertIn("8.0h", email_text)
        self.assertIn("85%", email_text)  # Formatted as 85%
        self.assertIn("10:00", email_text)


if __name__ == "__main__":
    unittest.main()
