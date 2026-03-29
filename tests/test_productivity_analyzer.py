"""
Unit Tests for Productivity Analyzer Module

Feature 4: Productivity Insights
Tests: Analyzer core functionality, metrics, patterns, insights, reports
"""

import unittest
import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from productivity_analyzer import (
    ProductivityAnalyzer, ProductivityMetric,
    WorkPattern, ProductivityInsight, ProductivityReport
)


class TestProductivityMetric(unittest.TestCase):
    """Test ProductivityMetric dataclass."""
    
    def test_create_metric(self):
        """Test creating a metric."""
        metric = ProductivityMetric(
            employee_id="emp-001",
            metric_name="focus_score",
            value=85.5,
            measurement_date="2026-03-28"
        )
        
        self.assertEqual(metric.employee_id, "emp-001")
        self.assertEqual(metric.metric_name, "focus_score")
        self.assertEqual(metric.value, 85.5)
    
    def test_metric_to_dict(self):
        """Test converting metric to dict."""
        metric = ProductivityMetric(
            employee_id="emp-001",
            metric_name="focus_score",
            value=85.5,
            measurement_date="2026-03-28"
        )
        
        data = metric.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["employee_id"], "emp-001")
        self.assertEqual(data["value"], 85.5)
    
    def test_metric_from_dict(self):
        """Test creating metric from dict."""
        data = {
            "metric_id": "m1",
            "employee_id": "emp-001",
            "metric_name": "focus_score",
            "value": 85.5,
            "measurement_date": "2026-03-28",
            "calculated_at": "2026-03-28T10:00:00Z"
        }
        
        metric = ProductivityMetric.from_dict(data)
        self.assertEqual(metric.employee_id, "emp-001")
        self.assertEqual(metric.value, 85.5)


class TestWorkPattern(unittest.TestCase):
    """Test WorkPattern dataclass."""
    
    def test_create_pattern(self):
        """Test creating a pattern."""
        pattern = WorkPattern(
            employee_id="emp-001",
            pattern_type="peak_hours",
            description="Peak productivity from 9-11 AM",
            confidence=0.85
        )
        
        self.assertEqual(pattern.pattern_type, "peak_hours")
        self.assertEqual(pattern.confidence, 0.85)
    
    def test_pattern_to_dict(self):
        """Test converting pattern to dict."""
        pattern = WorkPattern(
            employee_id="emp-001",
            pattern_type="peak_hours",
            description="Test pattern",
            confidence=0.85
        )
        
        data = pattern.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["pattern_type"], "peak_hours")


class TestProductivityInsight(unittest.TestCase):
    """Test ProductivityInsight dataclass."""
    
    def test_create_insight(self):
        """Test creating an insight."""
        insight = ProductivityInsight(
            employee_id="emp-001",
            title="Strong Focus",
            description="High focus score",
            insight_type="strength",
            confidence=0.9
        )
        
        self.assertEqual(insight.title, "Strong Focus")
        self.assertEqual(insight.insight_type, "strength")
    
    def test_insight_to_dict(self):
        """Test converting insight to dict."""
        insight = ProductivityInsight(
            employee_id="emp-001",
            title="Test Insight",
            description="Test",
            insight_type="strength",
            confidence=0.9
        )
        
        data = insight.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["title"], "Test Insight")


class TestProductivityReport(unittest.TestCase):
    """Test ProductivityReport dataclass."""
    
    def test_create_report(self):
        """Test creating a report."""
        report = ProductivityReport(
            employee_id="emp-001",
            employee_name="John Doe",
            period_start="2026-03-21",
            period_end="2026-03-28",
            overall_score=85
        )
        
        self.assertEqual(report.employee_id, "emp-001")
        self.assertEqual(report.overall_score, 85)
        self.assertEqual(report.status, "generated")
    
    def test_report_to_dict(self):
        """Test converting report to dict."""
        report = ProductivityReport(
            employee_id="emp-001",
            employee_name="John Doe",
            period_start="2026-03-21",
            period_end="2026-03-28",
            overall_score=85
        )
        
        data = report.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["overall_score"], 85)


class TestProductivityAnalyzer(unittest.TestCase):
    """Test ProductivityAnalyzer core functionality."""
    
    def setUp(self):
        """Set up test analyzer with temp directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = ProductivityAnalyzer(self.temp_dir)
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        self.assertIsNotNone(self.analyzer)
        self.assertTrue(self.analyzer.data_dir.exists())
    
    def test_add_metric(self):
        """Test adding a metric."""
        metric = ProductivityMetric(
            employee_id="emp-001",
            metric_name="focus_score",
            value=85,
            measurement_date="2026-03-28"
        )
        
        metric_id = self.analyzer.add_metric(metric)
        self.assertIsNotNone(metric_id)
        self.assertEqual(metric_id, metric.metric_id)
    
    def test_add_metric_invalid_name(self):
        """Test adding metric with invalid name."""
        metric = ProductivityMetric(
            employee_id="emp-001",
            metric_name="invalid_metric",
            value=85,
            measurement_date="2026-03-28"
        )
        
        with self.assertRaises(ValueError):
            self.analyzer.add_metric(metric)
    
    def test_add_metric_missing_employee_id(self):
        """Test adding metric without employee_id."""
        metric = ProductivityMetric(
            employee_id="",
            metric_name="focus_score",
            value=85,
            measurement_date="2026-03-28"
        )
        
        with self.assertRaises(ValueError):
            self.analyzer.add_metric(metric)
    
    def test_add_pattern(self):
        """Test adding a pattern."""
        pattern = WorkPattern(
            employee_id="emp-001",
            pattern_type="peak_hours",
            description="Peak productivity",
            confidence=0.85
        )
        
        pattern_id = self.analyzer.add_pattern(pattern)
        self.assertIsNotNone(pattern_id)
    
    def test_add_pattern_invalid_confidence(self):
        """Test pattern with invalid confidence."""
        pattern = WorkPattern(
            employee_id="emp-001",
            pattern_type="peak_hours",
            description="Test",
            confidence=1.5  # > 1.0
        )
        
        with self.assertRaises(ValueError):
            self.analyzer.add_pattern(pattern)
    
    def test_add_insight(self):
        """Test adding an insight."""
        insight = ProductivityInsight(
            employee_id="emp-001",
            title="Test Insight",
            description="Test",
            insight_type="strength",
            confidence=0.85
        )
        
        insight_id = self.analyzer.add_insight(insight)
        self.assertIsNotNone(insight_id)
    
    def test_add_insight_missing_title(self):
        """Test insight without title."""
        insight = ProductivityInsight(
            employee_id="emp-001",
            title="",
            description="Test",
            insight_type="strength",
            confidence=0.85
        )
        
        with self.assertRaises(ValueError):
            self.analyzer.add_insight(insight)
    
    def test_add_report(self):
        """Test adding a report."""
        report = ProductivityReport(
            employee_id="emp-001",
            employee_name="John Doe",
            period_start="2026-03-21",
            period_end="2026-03-28",
            overall_score=85
        )
        
        report_id = self.analyzer.add_report(report)
        self.assertIsNotNone(report_id)
    
    def test_get_metrics_for_employee(self):
        """Test retrieving metrics for employee."""
        # Add multiple metrics
        for i in range(3):
            metric = ProductivityMetric(
                employee_id="emp-001",
                metric_name="focus_score",
                value=80 + i,
                measurement_date="2026-03-28"
            )
            self.analyzer.add_metric(metric)
        
        metrics = self.analyzer.get_metrics_for_employee("emp-001")
        self.assertGreaterEqual(len(metrics), 3)
        self.assertTrue(all(m.employee_id == "emp-001" for m in metrics))
    
    def test_get_patterns_for_employee(self):
        """Test retrieving patterns for employee."""
        pattern = WorkPattern(
            employee_id="emp-001",
            pattern_type="peak_hours",
            description="Test",
            confidence=0.85
        )
        self.analyzer.add_pattern(pattern)
        
        patterns = self.analyzer.get_patterns_for_employee("emp-001")
        self.assertGreaterEqual(len(patterns), 1)
    
    def test_get_insights_for_employee(self):
        """Test retrieving insights for employee."""
        insight = ProductivityInsight(
            employee_id="emp-001",
            title="Test",
            description="Test",
            insight_type="strength",
            confidence=0.85
        )
        self.analyzer.add_insight(insight)
        
        insights = self.analyzer.get_insights_for_employee("emp-001")
        self.assertGreaterEqual(len(insights), 1)
    
    def test_get_report(self):
        """Test retrieving a report."""
        report = ProductivityReport(
            employee_id="emp-001",
            employee_name="John Doe",
            period_start="2026-03-21",
            period_end="2026-03-28",
            overall_score=85
        )
        
        report_id = self.analyzer.add_report(report)
        retrieved = self.analyzer.get_report(report_id)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.employee_id, "emp-001")
    
    def test_get_recent_reports(self):
        """Test retrieving recent reports."""
        for i in range(3):
            report = ProductivityReport(
                employee_id="emp-001",
                employee_name="John Doe",
                period_start="2026-03-21",
                period_end="2026-03-28",
                overall_score=80 + i
            )
            self.analyzer.add_report(report)
        
        reports = self.analyzer.get_recent_reports("emp-001", limit=2)
        self.assertEqual(len(reports), 2)
    
    def test_get_metrics_summary(self):
        """Test getting metrics summary."""
        # Add metrics with different values
        for value in [80, 85, 90]:
            metric = ProductivityMetric(
                employee_id="emp-001",
                metric_name="focus_score",
                value=value,
                measurement_date="2026-03-28"
            )
            self.analyzer.add_metric(metric)
        
        summary = self.analyzer.get_metrics_summary("emp-001")
        self.assertIn("focus_score_avg", summary)
        self.assertIn("focus_score_max", summary)
        self.assertIn("focus_score_min", summary)
    
    def test_clear_old_data(self):
        """Test clearing old data."""
        # Add metric
        metric = ProductivityMetric(
            employee_id="emp-001",
            metric_name="focus_score",
            value=85,
            measurement_date="2026-03-28"
        )
        self.analyzer.add_metric(metric)
        
        # Clear data older than 0 days (should remove recent data)
        count = self.analyzer.clear_old_data(days=0)
        self.assertGreater(count, 0)
    
    def test_data_statistics(self):
        """Test getting data statistics."""
        # Add some data
        metric = ProductivityMetric(
            employee_id="emp-001",
            metric_name="focus_score",
            value=85,
            measurement_date="2026-03-28"
        )
        self.analyzer.add_metric(metric)
        
        stats = self.analyzer.get_data_statistics()
        self.assertIn("metrics_count", stats)
        self.assertIn("patterns_count", stats)
        self.assertIn("insights_count", stats)
        self.assertGreaterEqual(stats["metrics_count"], 1)
    
    def test_persistence(self):
        """Test data persistence across instances."""
        # Add data to first analyzer
        metric = ProductivityMetric(
            employee_id="emp-001",
            metric_name="focus_score",
            value=85,
            measurement_date="2026-03-28"
        )
        self.analyzer.add_metric(metric)
        
        # Create new analyzer with same directory
        analyzer2 = ProductivityAnalyzer(self.temp_dir)
        metrics = analyzer2.get_metrics_for_employee("emp-001")
        
        self.assertGreaterEqual(len(metrics), 1)


if __name__ == "__main__":
    unittest.main()
