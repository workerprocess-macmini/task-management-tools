"""
Unit Tests for Insights Validators Module

Feature 4: Productivity Insights
Tests: Validation functions for all data types
"""

import unittest
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from insights_validators import (
    InsightValidationError,
    validate_employee_id,
    validate_metric_name,
    validate_metric_value,
    validate_pattern_type,
    validate_insight_type,
    validate_severity,
    validate_confidence,
    validate_date_string,
    validate_iso_timestamp,
    validate_period_type,
    validate_action_category,
    validate_impact_area,
    validate_report_overall_score,
    validate_report_trend,
    validate_metric_data,
    validate_insight_data,
    validate_report_data,
    validate_json_schema
)


class TestEmployeeIdValidation(unittest.TestCase):
    """Test employee ID validation."""
    
    def test_valid_employee_id(self):
        """Test valid employee IDs."""
        self.assertTrue(validate_employee_id("emp-001"))
        self.assertTrue(validate_employee_id("emp_001"))
        self.assertTrue(validate_employee_id("EMP001"))
    
    def test_invalid_employee_id_empty(self):
        """Test empty employee ID."""
        with self.assertRaises(InsightValidationError):
            validate_employee_id("")
    
    def test_invalid_employee_id_type(self):
        """Test non-string employee ID."""
        with self.assertRaises(InsightValidationError):
            validate_employee_id(123)
    
    def test_invalid_employee_id_special_chars(self):
        """Test employee ID with invalid characters."""
        with self.assertRaises(InsightValidationError):
            validate_employee_id("emp@001")
    
    def test_invalid_employee_id_too_long(self):
        """Test employee ID exceeding max length."""
        with self.assertRaises(InsightValidationError):
            validate_employee_id("a" * 101)


class TestMetricValidation(unittest.TestCase):
    """Test metric validation."""
    
    def test_valid_metric_names(self):
        """Test valid metric names."""
        valid_names = [
            "tasks_per_hour", "tasks_per_day", "avg_task_duration",
            "focus_score", "balance_score", "consistency_score",
            "peak_hours", "productive_hours", "break_frequency"
        ]
        for name in valid_names:
            self.assertTrue(validate_metric_name(name))
    
    def test_invalid_metric_name(self):
        """Test invalid metric name."""
        with self.assertRaises(InsightValidationError):
            validate_metric_name("invalid_metric")
    
    def test_valid_metric_values(self):
        """Test valid metric values."""
        self.assertTrue(validate_metric_value(0))
        self.assertTrue(validate_metric_value(50.5))
        self.assertTrue(validate_metric_value(100))
    
    def test_invalid_metric_value_negative(self):
        """Test negative metric value."""
        with self.assertRaises(InsightValidationError):
            validate_metric_value(-1)
    
    def test_invalid_metric_value_type(self):
        """Test non-numeric metric value."""
        with self.assertRaises(InsightValidationError):
            validate_metric_value("50")
    
    def test_focus_score_validation(self):
        """Test focus_score context validation."""
        self.assertTrue(validate_metric_value(50, "focus_score"))
        with self.assertRaises(InsightValidationError):
            validate_metric_value(150, "focus_score")


class TestPatternValidation(unittest.TestCase):
    """Test pattern type validation."""
    
    def test_valid_pattern_types(self):
        """Test valid pattern types."""
        valid_types = [
            "peak_hours", "low_hours", "category_focus", "break_pattern",
            "context_switching", "focus_blocks", "workload_trend",
            "consistency_pattern", "weekend_work", "overtime_pattern"
        ]
        for ptype in valid_types:
            self.assertTrue(validate_pattern_type(ptype))
    
    def test_invalid_pattern_type(self):
        """Test invalid pattern type."""
        with self.assertRaises(InsightValidationError):
            validate_pattern_type("invalid_pattern")


class TestInsightTypeValidation(unittest.TestCase):
    """Test insight type validation."""
    
    def test_valid_insight_types(self):
        """Test valid insight types."""
        valid_types = ["strength", "weakness", "opportunity", "pattern", "trend"]
        for itype in valid_types:
            self.assertTrue(validate_insight_type(itype))
    
    def test_invalid_insight_type(self):
        """Test invalid insight type."""
        with self.assertRaises(InsightValidationError):
            validate_insight_type("invalid")


class TestSeverityValidation(unittest.TestCase):
    """Test severity validation."""
    
    def test_valid_severities(self):
        """Test valid severity levels."""
        valid = ["info", "low", "medium", "high", "critical"]
        for sev in valid:
            self.assertTrue(validate_severity(sev))
    
    def test_invalid_severity(self):
        """Test invalid severity."""
        with self.assertRaises(InsightValidationError):
            validate_severity("invalid")


class TestConfidenceValidation(unittest.TestCase):
    """Test confidence validation."""
    
    def test_valid_confidence(self):
        """Test valid confidence scores."""
        self.assertTrue(validate_confidence(0.0))
        self.assertTrue(validate_confidence(0.5))
        self.assertTrue(validate_confidence(1.0))
    
    def test_invalid_confidence_too_high(self):
        """Test confidence > 1.0."""
        with self.assertRaises(InsightValidationError):
            validate_confidence(1.1)
    
    def test_invalid_confidence_too_low(self):
        """Test confidence < 0.0."""
        with self.assertRaises(InsightValidationError):
            validate_confidence(-0.1)
    
    def test_invalid_confidence_type(self):
        """Test non-numeric confidence."""
        with self.assertRaises(InsightValidationError):
            validate_confidence("0.5")


class TestDateValidation(unittest.TestCase):
    """Test date validation."""
    
    def test_valid_date(self):
        """Test valid date format."""
        self.assertTrue(validate_date_string("2026-03-28"))
    
    def test_invalid_date_format(self):
        """Test invalid date format."""
        with self.assertRaises(InsightValidationError):
            validate_date_string("03/28/2026")
    
    def test_invalid_date_empty(self):
        """Test empty date."""
        with self.assertRaises(InsightValidationError):
            validate_date_string("")
    
    def test_allow_empty_date(self):
        """Test allowing empty date."""
        self.assertTrue(validate_date_string("", allow_empty=True))


class TestTimestampValidation(unittest.TestCase):
    """Test ISO 8601 timestamp validation."""
    
    def test_valid_timestamp_with_timezone(self):
        """Test valid ISO timestamp with timezone."""
        self.assertTrue(validate_iso_timestamp("2026-03-28T10:30:00+07:00"))
    
    def test_valid_timestamp_with_z(self):
        """Test valid ISO timestamp with Z."""
        self.assertTrue(validate_iso_timestamp("2026-03-28T10:30:00Z"))
    
    def test_invalid_timestamp(self):
        """Test invalid timestamp."""
        with self.assertRaises(InsightValidationError):
            validate_iso_timestamp("2026-03-28 10:30:00")


class TestPeriodTypeValidation(unittest.TestCase):
    """Test period type validation."""
    
    def test_valid_period_types(self):
        """Test valid period types."""
        for ptype in ["daily", "weekly", "monthly"]:
            self.assertTrue(validate_period_type(ptype))
    
    def test_invalid_period_type(self):
        """Test invalid period type."""
        with self.assertRaises(InsightValidationError):
            validate_period_type("yearly")


class TestActionCategoryValidation(unittest.TestCase):
    """Test action category validation."""
    
    def test_valid_action_categories(self):
        """Test valid action categories."""
        valid = [
            "time_management", "focus", "breaks", "workload", "schedule",
            "optimization", "improvement", "health"
        ]
        for cat in valid:
            self.assertTrue(validate_action_category(cat))
    
    def test_invalid_action_category(self):
        """Test invalid action category."""
        with self.assertRaises(InsightValidationError):
            validate_action_category("invalid")


class TestImpactAreaValidation(unittest.TestCase):
    """Test impact area validation."""
    
    def test_valid_impact_areas(self):
        """Test valid impact areas."""
        valid = ["Productivity", "Health", "Quality", "Efficiency"]
        for area in valid:
            self.assertTrue(validate_impact_area(area))
    
    def test_invalid_impact_area(self):
        """Test invalid impact area."""
        with self.assertRaises(InsightValidationError):
            validate_impact_area("invalid")


class TestReportScoreValidation(unittest.TestCase):
    """Test report score validation."""
    
    def test_valid_score(self):
        """Test valid scores."""
        self.assertTrue(validate_report_overall_score(0))
        self.assertTrue(validate_report_overall_score(50))
        self.assertTrue(validate_report_overall_score(100))
    
    def test_invalid_score_too_high(self):
        """Test score > 100."""
        with self.assertRaises(InsightValidationError):
            validate_report_overall_score(101)
    
    def test_invalid_score_type(self):
        """Test non-numeric score."""
        with self.assertRaises(InsightValidationError):
            validate_report_overall_score("50")


class TestReportTrendValidation(unittest.TestCase):
    """Test report trend validation."""
    
    def test_valid_trends(self):
        """Test valid trend values."""
        for trend in ["improving", "stable", "declining"]:
            self.assertTrue(validate_report_trend(trend))
    
    def test_invalid_trend(self):
        """Test invalid trend."""
        with self.assertRaises(InsightValidationError):
            validate_report_trend("invalid")


class TestCompleteDataValidation(unittest.TestCase):
    """Test validation of complete data objects."""
    
    def test_valid_metric_data(self):
        """Test valid metric data."""
        data = {
            "employee_id": "emp-001",
            "metric_name": "focus_score",
            "value": 85,
            "measurement_date": "2026-03-28"
        }
        self.assertTrue(validate_metric_data(data))
    
    def test_invalid_metric_data_missing_field(self):
        """Test metric data with missing field."""
        data = {
            "employee_id": "emp-001",
            "metric_name": "focus_score"
        }
        with self.assertRaises(InsightValidationError):
            validate_metric_data(data)
    
    def test_valid_insight_data(self):
        """Test valid insight data."""
        data = {
            "employee_id": "emp-001",
            "title": "Test Insight",
            "description": "Test description",
            "insight_type": "strength",
            "confidence": 0.85
        }
        self.assertTrue(validate_insight_data(data))
    
    def test_invalid_insight_data_empty_title(self):
        """Test insight with empty title."""
        data = {
            "employee_id": "emp-001",
            "title": "",
            "description": "Test",
            "insight_type": "strength",
            "confidence": 0.85
        }
        with self.assertRaises(InsightValidationError):
            validate_insight_data(data)
    
    def test_valid_report_data(self):
        """Test valid report data."""
        data = {
            "employee_id": "emp-001",
            "period_start": "2026-03-21",
            "period_end": "2026-03-28",
            "overall_score": 85
        }
        self.assertTrue(validate_report_data(data))


class TestJsonSchemaValidation(unittest.TestCase):
    """Test JSON schema validation."""
    
    def test_valid_json(self):
        """Test valid JSON."""
        self.assertTrue(validate_json_schema('{"key": "value"}'))
    
    def test_invalid_json(self):
        """Test invalid JSON."""
        with self.assertRaises(InsightValidationError):
            validate_json_schema('{invalid}')


if __name__ == "__main__":
    unittest.main()
