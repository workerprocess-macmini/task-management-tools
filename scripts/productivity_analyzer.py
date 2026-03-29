"""
Productivity Analyzer Module for Work Logging System
Analyzes work patterns and generates actionable productivity insights.

Feature 4: Productivity Insights - Core Analysis Engine
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
import uuid
from statistics import mean, median, stdev


@dataclass
class WorkPattern:
    """Represents a detected work pattern."""
    
    pattern_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str = ""
    pattern_type: str = ""  # peak_hours, category_focus, break_pattern, etc.
    description: str = ""
    confidence: float = 0.0  # 0.0-1.0 confidence score
    
    # Pattern data
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    analysis_period_start: str = ""  # YYYY-MM-DD
    analysis_period_end: str = ""    # YYYY-MM-DD
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> WorkPattern:
        """Create from dictionary."""
        return WorkPattern(**data)


@dataclass
class ProductivityMetric:
    """Represents a single productivity metric."""
    
    metric_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str = ""
    metric_name: str = ""  # tasks_per_hour, focus_score, balance_score, etc.
    value: float = 0.0
    unit: str = ""
    
    # Context
    measurement_date: str = ""  # YYYY-MM-DD
    period_type: str = "daily"  # daily, weekly, monthly
    is_positive_trend: bool = True  # Whether increase is good
    
    # Comparison
    historical_average: Optional[float] = None
    variance_from_average: Optional[float] = None  # +/- percentage
    
    # Metadata
    calculated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> ProductivityMetric:
        """Create from dictionary."""
        return ProductivityMetric(**data)


@dataclass
class ProductivityInsight:
    """Represents a single productivity insight."""
    
    insight_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str = ""
    
    # Core insight
    title: str = ""
    description: str = ""
    insight_type: str = ""  # strength, weakness, opportunity, pattern, trend
    severity: str = "info"  # info, low, medium, high, critical
    
    # Evidence
    supported_by: List[str] = field(default_factory=list)  # Metric IDs
    confidence: float = 0.0  # 0.0-1.0
    
    # Recommendation
    recommended_action: str = ""
    action_category: str = ""  # time_management, focus, breaks, workload, etc.
    
    # Impact
    potential_impact: str = ""  # High, Medium, Low
    impact_area: str = ""  # Productivity, Health, Quality, Efficiency
    
    # Metadata
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    analysis_date: str = ""  # YYYY-MM-DD
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> ProductivityInsight:
        """Create from dictionary."""
        return ProductivityInsight(**data)


@dataclass
class ProductivityReport:
    """Complete productivity analysis report."""
    
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str = ""
    employee_name: str = ""
    
    # Report period
    period_start: str = ""  # YYYY-MM-DD
    period_end: str = ""    # YYYY-MM-DD
    period_type: str = "weekly"  # daily, weekly, monthly
    
    # Analysis results
    metrics: List[ProductivityMetric] = field(default_factory=list)
    patterns: List[WorkPattern] = field(default_factory=list)
    insights: List[ProductivityInsight] = field(default_factory=list)
    
    # Summary statistics
    overall_score: float = 0.0  # 0-100
    trend: str = "stable"  # improving, stable, declining
    score_change: float = 0.0  # +/- percentage from previous period
    
    # Top findings
    top_strengths: List[str] = field(default_factory=list)
    top_opportunities: List[str] = field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    priority_actions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Report metadata
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    analysis_count: int = 0
    data_quality: float = 1.0  # 0.0-1.0, how complete the data was
    
    # Status
    status: str = "generated"  # generated, reviewed, archived
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> ProductivityReport:
        """Create from dictionary."""
        return ProductivityReport(**data)


class ProductivityAnalyzer:
    """
    Core analysis engine for productivity insights.
    
    Analyzes work data to detect patterns, calculate metrics,
    and generate actionable insights.
    """
    
    # Valid metric names
    VALID_METRICS = {
        "tasks_per_hour", "tasks_per_day", "avg_task_duration",
        "focus_score", "balance_score", "consistency_score",
        "peak_hours", "productive_hours", "break_frequency",
        "category_distribution", "priority_distribution",
        "completion_rate", "context_switches", "deep_work_hours"
    }
    
    # Valid insight types
    VALID_INSIGHT_TYPES = {"strength", "weakness", "opportunity", "pattern", "trend"}
    
    # Valid pattern types
    VALID_PATTERN_TYPES = {
        "peak_hours", "low_hours", "category_focus", "break_pattern",
        "context_switching", "focus_blocks", "workload_trend",
        "consistency_pattern", "weekend_work", "overtime_pattern"
    }
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the productivity analyzer.
        
        Args:
            data_dir: Directory for storing analysis data
        """
        self.data_dir = Path(data_dir) if data_dir else Path.home() / ".work-logging" / "insights"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self._lock = threading.RLock()
        self._metrics: Dict[str, ProductivityMetric] = {}
        self._patterns: Dict[str, WorkPattern] = {}
        self._insights: Dict[str, ProductivityInsight] = {}
        self._reports: Dict[str, ProductivityReport] = {}
        
        self._load_all()
    
    def _load_all(self) -> None:
        """Load all analysis data from files."""
        with self._lock:
            try:
                metrics_file = self.data_dir / "metrics.json"
                if metrics_file.exists():
                    data = json.loads(metrics_file.read_text())
                    self._metrics = {m["metric_id"]: ProductivityMetric.from_dict(m) for m in data.get("metrics", [])}
                
                patterns_file = self.data_dir / "patterns.json"
                if patterns_file.exists():
                    data = json.loads(patterns_file.read_text())
                    self._patterns = {p["pattern_id"]: WorkPattern.from_dict(p) for p in data.get("patterns", [])}
                
                insights_file = self.data_dir / "insights.json"
                if insights_file.exists():
                    data = json.loads(insights_file.read_text())
                    self._insights = {i["insight_id"]: ProductivityInsight.from_dict(i) for i in data.get("insights", [])}
                
                reports_file = self.data_dir / "reports.json"
                if reports_file.exists():
                    data = json.loads(reports_file.read_text())
                    self._reports = {r["report_id"]: ProductivityReport.from_dict(r) for r in data.get("reports", [])}
            except Exception:
                pass  # Start fresh if load fails
    
    def _save_all(self) -> None:
        """Save all analysis data to files."""
        with self._lock:
            try:
                (self.data_dir / "metrics.json").write_text(
                    json.dumps({
                        "metrics": [m.to_dict() for m in self._metrics.values()],
                        "saved_at": datetime.now(timezone.utc).isoformat(),
                        "count": len(self._metrics)
                    }, indent=2)
                )
                (self.data_dir / "patterns.json").write_text(
                    json.dumps({
                        "patterns": [p.to_dict() for p in self._patterns.values()],
                        "saved_at": datetime.now(timezone.utc).isoformat(),
                        "count": len(self._patterns)
                    }, indent=2)
                )
                (self.data_dir / "insights.json").write_text(
                    json.dumps({
                        "insights": [i.to_dict() for i in self._insights.values()],
                        "saved_at": datetime.now(timezone.utc).isoformat(),
                        "count": len(self._insights)
                    }, indent=2)
                )
                (self.data_dir / "reports.json").write_text(
                    json.dumps({
                        "reports": [r.to_dict() for r in self._reports.values()],
                        "saved_at": datetime.now(timezone.utc).isoformat(),
                        "count": len(self._reports)
                    }, indent=2)
                )
            except Exception:
                pass  # Silently fail if save fails
    
    def add_metric(self, metric: ProductivityMetric) -> str:
        """
        Add a productivity metric.
        
        Args:
            metric: The metric to add
            
        Returns:
            The metric ID
            
        Raises:
            ValueError: If metric data is invalid
        """
        with self._lock:
            if not metric.metric_name or metric.metric_name not in self.VALID_METRICS:
                raise ValueError(f"Invalid metric name: {metric.metric_name}")
            if not metric.employee_id:
                raise ValueError("employee_id is required")
            if metric.value < 0:
                raise ValueError("metric value cannot be negative")
            
            self._metrics[metric.metric_id] = metric
            self._save_all()
            return metric.metric_id
    
    def add_pattern(self, pattern: WorkPattern) -> str:
        """
        Add a work pattern.
        
        Args:
            pattern: The pattern to add
            
        Returns:
            The pattern ID
            
        Raises:
            ValueError: If pattern data is invalid
        """
        with self._lock:
            if not pattern.pattern_type or pattern.pattern_type not in self.VALID_PATTERN_TYPES:
                raise ValueError(f"Invalid pattern type: {pattern.pattern_type}")
            if not pattern.employee_id:
                raise ValueError("employee_id is required")
            if not (0 <= pattern.confidence <= 1.0):
                raise ValueError("confidence must be between 0.0 and 1.0")
            
            self._patterns[pattern.pattern_id] = pattern
            self._save_all()
            return pattern.pattern_id
    
    def add_insight(self, insight: ProductivityInsight) -> str:
        """
        Add a productivity insight.
        
        Args:
            insight: The insight to add
            
        Returns:
            The insight ID
            
        Raises:
            ValueError: If insight data is invalid
        """
        with self._lock:
            if not insight.insight_type or insight.insight_type not in self.VALID_INSIGHT_TYPES:
                raise ValueError(f"Invalid insight type: {insight.insight_type}")
            if not insight.employee_id:
                raise ValueError("employee_id is required")
            if not insight.title:
                raise ValueError("title is required")
            if not (0 <= insight.confidence <= 1.0):
                raise ValueError("confidence must be between 0.0 and 1.0")
            
            self._insights[insight.insight_id] = insight
            self._save_all()
            return insight.insight_id
    
    def add_report(self, report: ProductivityReport) -> str:
        """
        Add a productivity report.
        
        Args:
            report: The report to add
            
        Returns:
            The report ID
            
        Raises:
            ValueError: If report data is invalid
        """
        with self._lock:
            if not report.employee_id:
                raise ValueError("employee_id is required")
            if not report.period_start or not report.period_end:
                raise ValueError("period_start and period_end are required")
            if not (0 <= report.overall_score <= 100):
                raise ValueError("overall_score must be between 0 and 100")
            
            self._reports[report.report_id] = report
            self._save_all()
            return report.report_id
    
    def get_metrics_for_employee(self, employee_id: str, days: int = 7) -> List[ProductivityMetric]:
        """
        Get recent metrics for an employee.
        
        Args:
            employee_id: The employee ID
            days: Number of days to look back
            
        Returns:
            List of matching metrics
        """
        with self._lock:
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            return [
                m for m in self._metrics.values()
                if m.employee_id == employee_id and m.calculated_at >= cutoff_date
            ]
    
    def get_patterns_for_employee(self, employee_id: str) -> List[WorkPattern]:
        """
        Get work patterns for an employee.
        
        Args:
            employee_id: The employee ID
            
        Returns:
            List of matching patterns
        """
        with self._lock:
            return [p for p in self._patterns.values() if p.employee_id == employee_id]
    
    def get_insights_for_employee(self, employee_id: str, days: int = 7) -> List[ProductivityInsight]:
        """
        Get recent insights for an employee.
        
        Args:
            employee_id: The employee ID
            days: Number of days to look back
            
        Returns:
            List of matching insights
        """
        with self._lock:
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            return [
                i for i in self._insights.values()
                if i.employee_id == employee_id and i.generated_at >= cutoff_date
            ]
    
    def get_report(self, report_id: str) -> Optional[ProductivityReport]:
        """
        Get a productivity report by ID.
        
        Args:
            report_id: The report ID
            
        Returns:
            The report, or None if not found
        """
        with self._lock:
            return self._reports.get(report_id)
    
    def get_recent_reports(self, employee_id: str, limit: int = 10) -> List[ProductivityReport]:
        """
        Get recent reports for an employee.
        
        Args:
            employee_id: The employee ID
            limit: Maximum number of reports to return
            
        Returns:
            List of matching reports, most recent first
        """
        with self._lock:
            reports = [r for r in self._reports.values() if r.employee_id == employee_id]
            return sorted(reports, key=lambda r: r.generated_at, reverse=True)[:limit]
    
    def get_metrics_summary(self, employee_id: str) -> Dict[str, float]:
        """
        Get summary statistics for an employee's metrics.
        
        Args:
            employee_id: The employee ID
            
        Returns:
            Dictionary of metric name to value
        """
        with self._lock:
            metrics = self.get_metrics_for_employee(employee_id, days=30)
            summary: Dict[str, List[float]] = {}
            
            for metric in metrics:
                if metric.metric_name not in summary:
                    summary[metric.metric_name] = []
                summary[metric.metric_name].append(metric.value)
            
            result = {}
            for name, values in summary.items():
                if values:
                    result[f"{name}_avg"] = mean(values)
                    result[f"{name}_max"] = max(values)
                    result[f"{name}_min"] = min(values)
                    if len(values) > 1:
                        result[f"{name}_stdev"] = stdev(values)
            
            return result
    
    def clear_old_data(self, days: int = 90) -> int:
        """
        Clear data older than specified days.
        
        Args:
            days: Age threshold in days
            
        Returns:
            Number of items removed
        """
        with self._lock:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            count = 0
            
            # Remove old metrics
            old_metrics = [mid for mid, m in self._metrics.items() if m.calculated_at < cutoff]
            for mid in old_metrics:
                del self._metrics[mid]
                count += 1
            
            # Remove old patterns
            old_patterns = [pid for pid, p in self._patterns.items() if p.detected_at < cutoff]
            for pid in old_patterns:
                del self._patterns[pid]
                count += 1
            
            # Remove old insights
            old_insights = [iid for iid, i in self._insights.items() if i.generated_at < cutoff]
            for iid in old_insights:
                del self._insights[iid]
                count += 1
            
            self._save_all()
            return count
    
    def get_data_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored data.
        
        Returns:
            Dictionary with data counts and status
        """
        with self._lock:
            return {
                "metrics_count": len(self._metrics),
                "patterns_count": len(self._patterns),
                "insights_count": len(self._insights),
                "reports_count": len(self._reports),
                "total_items": len(self._metrics) + len(self._patterns) + len(self._insights) + len(self._reports),
                "data_dir": str(self.data_dir),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
