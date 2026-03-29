"""
Unit Tests for Insights Generators Module

Feature 4: Productivity Insights
Tests: Insight generation, trend analysis, recommendations
"""

import unittest
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from productivity_analyzer import (
    ProductivityAnalyzer, ProductivityMetric, ProductivityInsight
)
from insights_generators import (
    InsightsGenerator, RecommendationsGenerator
)


class TestInsightsGenerator(unittest.TestCase):
    """Test InsightsGenerator functionality."""
    
    def setUp(self):
        """Set up test generator."""
        temp_dir = tempfile.mkdtemp()
        self.analyzer = ProductivityAnalyzer(temp_dir)
        self.generator = InsightsGenerator(self.analyzer)
    
    def test_generator_initialization(self):
        """Test generator initialization."""
        self.assertIsNotNone(self.generator)
        self.assertIsNotNone(self.generator.analyzer)
    
    def test_generate_daily_insight_high_focus(self):
        """Test generating daily insight for high focus."""
        metrics = {
            "tasks_completed": 8,
            "focus_score": 85,
            "hours_worked": 8
        }
        
        insight = self.generator.generate_daily_insight("emp-001", metrics)
        
        self.assertIsNotNone(insight)
        self.assertEqual(insight.insight_type, "strength")
        self.assertEqual(insight.action_category, "focus")
    
    def test_generate_daily_insight_moderate_focus(self):
        """Test generating daily insight for moderate focus."""
        metrics = {
            "tasks_completed": 6,
            "focus_score": 65,
            "hours_worked": 8
        }
        
        insight = self.generator.generate_daily_insight("emp-001", metrics)
        
        self.assertIsNotNone(insight)
        self.assertEqual(insight.insight_type, "pattern")
    
    def test_generate_daily_insight_low_focus(self):
        """Test generating daily insight for low focus."""
        metrics = {
            "tasks_completed": 3,
            "focus_score": 40,
            "hours_worked": 8
        }
        
        insight = self.generator.generate_daily_insight("emp-001", metrics)
        
        self.assertIsNotNone(insight)
        self.assertEqual(insight.insight_type, "weakness")
    
    def test_generate_daily_insight_empty_metrics(self):
        """Test generating insight with empty metrics."""
        insight = self.generator.generate_daily_insight("emp-001", {})
        self.assertIsNone(insight)
    
    def test_generate_trend_insights_insufficient_data(self):
        """Test trend analysis with insufficient data."""
        insights = self.generator.generate_trend_insights("emp-001", [])
        self.assertEqual(len(insights), 0)
    
    def test_generate_trend_insights_improving(self):
        """Test detecting improving trend."""
        # Create improving trend: 50 -> 75 -> 90
        metrics = [
            ProductivityMetric(
                employee_id="emp-001",
                metric_name="focus_score",
                value=50,
                measurement_date="2026-03-20"
            ),
            ProductivityMetric(
                employee_id="emp-001",
                metric_name="focus_score",
                value=75,
                measurement_date="2026-03-25"
            ),
            ProductivityMetric(
                employee_id="emp-001",
                metric_name="focus_score",
                value=90,
                measurement_date="2026-03-28"
            )
        ]
        
        insights = self.generator.generate_trend_insights("emp-001", metrics)
        
        self.assertGreater(len(insights), 0)
        strength_insights = [i for i in insights if i.insight_type == "strength"]
        self.assertGreater(len(strength_insights), 0)
    
    def test_generate_trend_insights_declining(self):
        """Test detecting declining trend."""
        # Create declining trend: 90 -> 75 -> 50
        metrics = [
            ProductivityMetric(
                employee_id="emp-001",
                metric_name="focus_score",
                value=90,
                measurement_date="2026-03-20"
            ),
            ProductivityMetric(
                employee_id="emp-001",
                metric_name="focus_score",
                value=75,
                measurement_date="2026-03-25"
            ),
            ProductivityMetric(
                employee_id="emp-001",
                metric_name="focus_score",
                value=50,
                measurement_date="2026-03-28"
            )
        ]
        
        insights = self.generator.generate_trend_insights("emp-001", metrics)
        
        self.assertGreater(len(insights), 0)
        weakness_insights = [i for i in insights if i.insight_type == "weakness"]
        self.assertGreater(len(weakness_insights), 0)
    
    def test_generate_work_balance_insights_high_workload(self):
        """Test detecting high workload."""
        summaries = [
            {"total_work_hours": 10, "is_weekend": False},
            {"total_work_hours": 10.5, "is_weekend": False},
            {"total_work_hours": 11, "is_weekend": False},
            {"total_work_hours": 10, "is_weekend": False},
            {"total_work_hours": 9, "is_weekend": False}
        ]
        
        insights = self.generator.generate_work_balance_insights("emp-001", summaries)
        
        self.assertGreater(len(insights), 0)
        overwork_insights = [i for i in insights if "High Workload" in i.title]
        self.assertGreater(len(overwork_insights), 0)
    
    def test_generate_work_balance_insights_weekend_work(self):
        """Test detecting weekend work."""
        summaries = [
            {"total_work_hours": 8, "is_weekend": False},
            {"total_work_hours": 8, "is_weekend": False},
            {"total_work_hours": 4, "is_weekend": True},
            {"total_work_hours": 8, "is_weekend": False},
            {"total_work_hours": 8, "is_weekend": False}
        ]
        
        insights = self.generator.generate_work_balance_insights("emp-001", summaries)
        
        weekend_insights = [i for i in insights if "Weekend" in i.title]
        self.assertGreater(len(weekend_insights), 0)
    
    def test_generate_work_balance_insights_consistent_schedule(self):
        """Test detecting consistent work schedule."""
        summaries = [
            {"total_work_hours": 8, "is_weekend": False},
            {"total_work_hours": 8.1, "is_weekend": False},
            {"total_work_hours": 7.9, "is_weekend": False},
            {"total_work_hours": 8, "is_weekend": False},
            {"total_work_hours": 8.2, "is_weekend": False}
        ]
        
        insights = self.generator.generate_work_balance_insights("emp-001", summaries)
        
        consistency_insights = [i for i in insights if "Consistent" in i.title]
        self.assertGreater(len(consistency_insights), 0)
    
    def test_generate_focus_insights_long_sessions(self):
        """Test detecting long focus sessions."""
        sessions = [
            {"duration_minutes": 90, "pause_count": 1},
            {"duration_minutes": 85, "pause_count": 1},
            {"duration_minutes": 95, "pause_count": 1},
            {"duration_minutes": 80, "pause_count": 1}
        ]
        
        insights = self.generator.generate_focus_insights("emp-001", sessions)
        
        long_session_insights = [i for i in insights if "Long Focus" in i.title]
        self.assertGreater(len(long_session_insights), 0)
    
    def test_generate_focus_insights_short_sessions(self):
        """Test detecting frequent context switches."""
        sessions = [
            {"duration_minutes": 20, "pause_count": 2},
            {"duration_minutes": 15, "pause_count": 2},
            {"duration_minutes": 25, "pause_count": 3},
            {"duration_minutes": 18, "pause_count": 2}
        ]
        
        insights = self.generator.generate_focus_insights("emp-001", sessions)
        
        switch_insights = [i for i in insights if "Context Switch" in i.title]
        self.assertGreater(len(switch_insights), 0)
    
    def test_generate_focus_insights_healthy_breaks(self):
        """Test detecting healthy break patterns."""
        sessions = [
            {"duration_minutes": 50, "pause_count": 1},
            {"duration_minutes": 55, "pause_count": 1},
            {"duration_minutes": 60, "pause_count": 2},
            {"duration_minutes": 50, "pause_count": 1}
        ]
        
        insights = self.generator.generate_focus_insights("emp-001", sessions)
        
        break_insights = [i for i in insights if "Healthy Break" in i.title]
        self.assertGreater(len(break_insights), 0)
    
    def test_generate_category_insights_heavy_focus(self):
        """Test detecting heavy category focus."""
        distribution = {
            "development": 75,
            "testing": 15,
            "documentation": 10
        }
        
        insights = self.generator.generate_category_insights("emp-001", distribution)
        
        focus_insights = [i for i in insights if "Heavy" in i.title]
        self.assertGreater(len(focus_insights), 0)
    
    def test_generate_category_insights_balanced(self):
        """Test detecting balanced work distribution."""
        distribution = {
            "development": 35,
            "testing": 35,
            "documentation": 30
        }
        
        insights = self.generator.generate_category_insights("emp-001", distribution)
        
        balance_insights = [i for i in insights if "Balanced" in i.title]
        self.assertGreater(len(balance_insights), 0)


class TestRecommendationsGenerator(unittest.TestCase):
    """Test RecommendationsGenerator functionality."""
    
    def test_generate_recommendations(self):
        """Test generating recommendations from insights."""
        insights = [
            ProductivityInsight(
                employee_id="emp-001",
                title="Test 1",
                description="Test",
                insight_type="strength",
                confidence=0.9,
                recommended_action="Action 1"
            ),
            ProductivityInsight(
                employee_id="emp-001",
                title="Test 2",
                description="Test",
                insight_type="weakness",
                confidence=0.8,
                recommended_action="Action 2"
            )
        ]
        
        recommendations = RecommendationsGenerator.generate_recommendations(insights)
        
        self.assertGreater(len(recommendations), 0)
        self.assertIn("Action 1", recommendations)
    
    def test_generate_recommendations_empty_insights(self):
        """Test generating recommendations from empty insights."""
        recommendations = RecommendationsGenerator.generate_recommendations([])
        self.assertEqual(len(recommendations), 0)
    
    def test_prioritize_actions(self):
        """Test prioritizing actions."""
        insights = [
            ProductivityInsight(
                employee_id="emp-001",
                title="Critical",
                description="Test",
                insight_type="weakness",
                confidence=0.9,
                severity="critical",
                recommended_action="Fix immediately",
                action_category="focus"
            ),
            ProductivityInsight(
                employee_id="emp-001",
                title="Low",
                description="Test",
                insight_type="opportunity",
                confidence=0.7,
                severity="low",
                recommended_action="Optional action",
                action_category="optimization"
            )
        ]
        
        actions = RecommendationsGenerator.prioritize_actions(insights)
        
        self.assertEqual(len(actions), 2)
        # Critical should be first
        self.assertEqual(actions[0]["priority"], 1)
        self.assertEqual(actions[1]["priority"], 3)
    
    def test_prioritize_actions_correct_priority_order(self):
        """Test that actions are correctly ordered by priority."""
        insights = [
            ProductivityInsight(
                employee_id="emp-001",
                title="Medium",
                description="Test",
                insight_type="weakness",
                severity="medium",
                recommended_action="Medium action",
                action_category="focus",
                confidence=0.8
            ),
            ProductivityInsight(
                employee_id="emp-001",
                title="High",
                description="Test",
                insight_type="weakness",
                severity="high",
                recommended_action="High action",
                action_category="focus",
                confidence=0.85
            )
        ]
        
        actions = RecommendationsGenerator.prioritize_actions(insights)
        
        # High priority should come before medium
        self.assertEqual(actions[0]["priority"], 1)  # high
        self.assertEqual(actions[1]["priority"], 2)  # medium


if __name__ == "__main__":
    unittest.main()
