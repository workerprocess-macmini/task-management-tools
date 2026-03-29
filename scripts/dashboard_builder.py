"""
Team Performance Dashboard Builder
Feature 2: Team Performance Dashboard

Visualizes team work patterns, productivity metrics, and progress tracking.
Provides real-time dashboard data for team management and insights.

Responsibilities:
- Build dashboard structure from employee work data
- Calculate team metrics and aggregates
- Format data for dashboard visualization
- Support real-time updates and filtering
- Handle time-based aggregations (daily, weekly, monthly)
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
import uuid


@dataclass
class TeamMetric:
    """Represents a single team metric (e.g., productivity, utilization)."""
    
    metric_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""  # e.g., "avg_productivity", "team_utilization"
    value: float = 0.0  # Numeric value
    unit: str = ""  # e.g., "%", "hours", "tasks"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Metadata
    category: str = ""  # e.g., "productivity", "utilization", "quality"
    period: str = "daily"  # daily, weekly, monthly, real-time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> TeamMetric:
        """Create TeamMetric from dictionary."""
        return TeamMetric(**data)


@dataclass
class EmployeeWorkPattern:
    """Represents an employee's work pattern and productivity."""
    
    employee_id: str = ""
    name: str = ""
    
    # Work statistics
    total_hours_logged: float = 0.0
    total_tasks_completed: int = 0
    avg_task_duration: float = 0.0  # in hours
    
    # Productivity metrics
    productivity_score: float = 0.0  # 0-100%
    utilization_rate: float = 0.0  # % of expected hours worked
    
    # Work pattern
    peak_hours: List[str] = field(default_factory=list)  # e.g., ["09:00-11:00", "14:00-16:00"]
    most_productive_day: str = ""  # Monday, Tuesday, etc.
    
    # Category breakdown
    category_breakdown: Dict[str, float] = field(default_factory=dict)  # e.g., {"development": 60.5, "testing": 30.2}
    
    # Real-time status
    current_status: str = "offline"  # online, in_session, paused, offline
    last_activity: str = ""  # ISO timestamp
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> EmployeeWorkPattern:
        """Create from dictionary."""
        return EmployeeWorkPattern(**data)


@dataclass
class DashboardSnapshot:
    """Represents a complete dashboard snapshot at a point in time."""
    
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Team metrics
    team_metrics: List[TeamMetric] = field(default_factory=list)
    
    # Employee patterns
    employee_patterns: Dict[str, EmployeeWorkPattern] = field(default_factory=dict)
    
    # Aggregates
    total_team_hours: float = 0.0
    total_tasks_completed: int = 0
    team_average_productivity: float = 0.0
    
    # Period info
    period: str = "daily"  # daily, weekly, monthly
    period_start: str = ""
    period_end: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert employee patterns to dict format
        data["employee_patterns"] = {
            emp_id: pattern.to_dict()
            for emp_id, pattern in self.employee_patterns.items()
        }
        data["team_metrics"] = [m.to_dict() for m in self.team_metrics]
        return data
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> DashboardSnapshot:
        """Create from dictionary."""
        # Reconstruct nested objects
        metrics = [TeamMetric.from_dict(m) for m in data.get("team_metrics", [])]
        patterns = {
            emp_id: EmployeeWorkPattern.from_dict(p)
            for emp_id, p in data.get("employee_patterns", {}).items()
        }
        
        return DashboardSnapshot(
            snapshot_id=data.get("snapshot_id", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            team_metrics=metrics,
            employee_patterns=patterns,
            total_team_hours=data.get("total_team_hours", 0.0),
            total_tasks_completed=data.get("total_tasks_completed", 0),
            team_average_productivity=data.get("team_average_productivity", 0.0),
            period=data.get("period", "daily"),
            period_start=data.get("period_start", ""),
            period_end=data.get("period_end", "")
        )


class DashboardBuilder:
    """Builds and manages team performance dashboard data."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize dashboard builder.
        
        Args:
            data_dir: Directory for storing dashboard snapshots. Defaults to ./dashboard_data
        """
        self.data_dir = data_dir or Path("./dashboard_data")
        self.data_dir.mkdir(exist_ok=True, parents=True)
        
        self.snapshots: Dict[str, DashboardSnapshot] = {}
        self.lock = threading.RLock()
        
        # Load existing snapshots
        self._load_snapshots()
    
    def _load_snapshots(self) -> None:
        """Load all dashboard snapshots from disk."""
        with self.lock:
            for snapshot_file in self.data_dir.glob("snapshot_*.json"):
                try:
                    with open(snapshot_file, "r") as f:
                        data = json.load(f)
                        snapshot = DashboardSnapshot.from_dict(data)
                        self.snapshots[snapshot.snapshot_id] = snapshot
                except (json.JSONDecodeError, ValueError):
                    pass
    
    def create_snapshot(
        self,
        employee_data: Dict[str, Dict[str, Any]],
        period: str = "daily",
        period_start: Optional[str] = None,
        period_end: Optional[str] = None
    ) -> DashboardSnapshot:
        """
        Create a new dashboard snapshot from employee work data.
        
        Args:
            employee_data: Dict mapping employee_id to work data
                Expected keys: total_hours, tasks_completed, category_breakdown, status, last_activity
            period: Aggregation period (daily, weekly, monthly)
            period_start: Start of period (ISO format)
            period_end: End of period (ISO format)
        
        Returns:
            DashboardSnapshot with calculated metrics and patterns
        """
        with self.lock:
            snapshot = DashboardSnapshot(period=period)
            
            # Set period dates
            if period_start:
                snapshot.period_start = period_start
            if period_end:
                snapshot.period_end = period_end
            
            # Build employee patterns
            total_team_hours = 0.0
            total_tasks = 0
            productivity_scores = []
            
            for emp_id, data in employee_data.items():
                pattern = EmployeeWorkPattern(
                    employee_id=emp_id,
                    name=data.get("name", emp_id),
                    total_hours_logged=data.get("total_hours", 0.0),
                    total_tasks_completed=data.get("tasks_completed", 0),
                    avg_task_duration=self._calc_avg_task_duration(
                        data.get("total_hours", 0.0),
                        data.get("tasks_completed", 0)
                    ),
                    productivity_score=data.get("productivity_score", 0.0),
                    utilization_rate=data.get("utilization_rate", 0.0),
                    category_breakdown=data.get("category_breakdown", {}),
                    current_status=data.get("status", "offline"),
                    last_activity=data.get("last_activity", "")
                )
                
                snapshot.employee_patterns[emp_id] = pattern
                total_team_hours += pattern.total_hours_logged
                total_tasks += pattern.total_tasks_completed
                if pattern.productivity_score > 0:
                    productivity_scores.append(pattern.productivity_score)
            
            # Calculate team aggregates
            snapshot.total_team_hours = total_team_hours
            snapshot.total_tasks_completed = total_tasks
            if productivity_scores:
                snapshot.team_average_productivity = sum(productivity_scores) / len(productivity_scores)
            
            # Create team metrics
            snapshot.team_metrics = self._build_team_metrics(snapshot, employee_data)
            
            # Store snapshot
            self.snapshots[snapshot.snapshot_id] = snapshot
            self._save_snapshot(snapshot)
            
            return snapshot
    
    def _calc_avg_task_duration(self, total_hours: float, tasks_completed: int) -> float:
        """Calculate average task duration in hours."""
        if tasks_completed <= 0:
            return 0.0
        return round(total_hours / tasks_completed, 2)
    
    def _build_team_metrics(
        self,
        snapshot: DashboardSnapshot,
        employee_data: Dict[str, Dict[str, Any]]
    ) -> List[TeamMetric]:
        """
        Build team-level metrics.
        
        Args:
            snapshot: Dashboard snapshot
            employee_data: Employee data for additional calculations
        
        Returns:
            List of TeamMetric objects
        """
        metrics: List[TeamMetric] = []
        
        # Metric 1: Team Productivity
        metrics.append(TeamMetric(
            name="team_average_productivity",
            value=snapshot.team_average_productivity,
            unit="%",
            category="productivity",
            period=snapshot.period
        ))
        
        # Metric 2: Total Team Hours
        metrics.append(TeamMetric(
            name="total_team_hours",
            value=snapshot.total_team_hours,
            unit="hours",
            category="utilization",
            period=snapshot.period
        ))
        
        # Metric 3: Total Tasks Completed
        metrics.append(TeamMetric(
            name="total_tasks_completed",
            value=float(snapshot.total_tasks_completed),
            unit="tasks",
            category="output",
            period=snapshot.period
        ))
        
        # Metric 4: Team Member Count
        metrics.append(TeamMetric(
            name="active_team_members",
            value=float(len(snapshot.employee_patterns)),
            unit="people",
            category="team_size",
            period=snapshot.period
        ))
        
        # Metric 5: Avg Hours per Member
        avg_hours = snapshot.total_team_hours / len(snapshot.employee_patterns) if snapshot.employee_patterns else 0.0
        metrics.append(TeamMetric(
            name="avg_hours_per_member",
            value=round(avg_hours, 2),
            unit="hours",
            category="utilization",
            period=snapshot.period
        ))
        
        # Metric 6: Avg Tasks per Member
        avg_tasks = snapshot.total_tasks_completed / len(snapshot.employee_patterns) if snapshot.employee_patterns else 0.0
        metrics.append(TeamMetric(
            name="avg_tasks_per_member",
            value=round(avg_tasks, 2),
            unit="tasks",
            category="output",
            period=snapshot.period
        ))
        
        return metrics
    
    def _save_snapshot(self, snapshot: DashboardSnapshot) -> Path:
        """Save snapshot to disk."""
        snapshot_path = self.data_dir / f"snapshot_{snapshot.snapshot_id}.json"
        with open(snapshot_path, "w") as f:
            json.dump(snapshot.to_dict(), f, indent=2)
        return snapshot_path
    
    def get_snapshot(self, snapshot_id: str) -> Optional[DashboardSnapshot]:
        """Get a specific snapshot by ID."""
        with self.lock:
            return self.snapshots.get(snapshot_id)
    
    def get_latest_snapshot(self) -> Optional[DashboardSnapshot]:
        """Get the most recent dashboard snapshot."""
        with self.lock:
            if not self.snapshots:
                return None
            return max(
                self.snapshots.values(),
                key=lambda s: s.timestamp
            )
    
    def list_snapshots(
        self,
        period: Optional[str] = None,
        limit: int = 10
    ) -> List[DashboardSnapshot]:
        """
        List snapshots with optional filtering.
        
        Args:
            period: Filter by period (daily, weekly, monthly)
            limit: Maximum number to return
        
        Returns:
            List of snapshots sorted by timestamp (newest first)
        """
        with self.lock:
            snapshots = list(self.snapshots.values())
            
            if period:
                snapshots = [s for s in snapshots if s.period == period]
            
            # Sort by timestamp (newest first)
            snapshots.sort(key=lambda s: s.timestamp, reverse=True)
            
            return snapshots[:limit]
    
    def get_employee_trend(
        self,
        employee_id: str,
        snapshots_count: int = 7
    ) -> List[EmployeeWorkPattern]:
        """
        Get an employee's work pattern trend over multiple snapshots.
        
        Args:
            employee_id: Employee ID
            snapshots_count: Number of snapshots to analyze
        
        Returns:
            List of EmployeeWorkPattern objects in chronological order
        """
        with self.lock:
            snapshots = self.list_snapshots(limit=snapshots_count)
            trends = []
            
            for snapshot in reversed(snapshots):
                if employee_id in snapshot.employee_patterns:
                    trends.append(snapshot.employee_patterns[employee_id])
            
            return trends
    
    def calculate_metric_change(
        self,
        metric_name: str,
        current_snapshot: Optional[DashboardSnapshot] = None,
        previous_snapshot: Optional[DashboardSnapshot] = None
    ) -> Optional[float]:
        """
        Calculate percentage change in a metric between two snapshots.
        
        Args:
            metric_name: Name of metric to compare
            current_snapshot: Current snapshot (defaults to latest)
            previous_snapshot: Previous snapshot (defaults to second-latest)
        
        Returns:
            Percentage change, or None if calculation not possible
        """
        with self.lock:
            if not current_snapshot:
                current_snapshot = self.get_latest_snapshot()
            if not current_snapshot:
                return None
            
            # Find metric in current snapshot
            current_metric = next(
                (m for m in current_snapshot.team_metrics if m.name == metric_name),
                None
            )
            if not current_metric or current_metric.value == 0:
                return None
            
            # Get previous snapshot if not provided
            if not previous_snapshot:
                snapshots = self.list_snapshots(limit=2)
                if len(snapshots) < 2:
                    return None
                previous_snapshot = snapshots[1]
            
            # Find metric in previous snapshot
            previous_metric = next(
                (m for m in previous_snapshot.team_metrics if m.name == metric_name),
                None
            )
            if not previous_metric or previous_metric.value == 0:
                return None
            
            # Calculate percentage change
            change = ((current_metric.value - previous_metric.value) / previous_metric.value) * 100
            return round(change, 2)


def format_dashboard_summary(snapshot: DashboardSnapshot) -> str:
    """
    Format dashboard snapshot as a readable summary.
    
    Args:
        snapshot: DashboardSnapshot to format
    
    Returns:
        Formatted string for display
    """
    lines = [
        f"=== Team Performance Dashboard ===",
        f"Period: {snapshot.period} ({snapshot.period_start} to {snapshot.period_end})",
        f"Snapshot ID: {snapshot.snapshot_id}",
        f"",
        f"📊 Team Aggregates:",
        f"  • Total Hours: {snapshot.total_team_hours:.1f} hours",
        f"  • Tasks Completed: {snapshot.total_tasks_completed} tasks",
        f"  • Avg Productivity: {snapshot.team_average_productivity:.1f}%",
        f"  • Team Members: {len(snapshot.employee_patterns)} active",
        f"",
        f"👥 Employee Patterns:",
    ]
    
    for emp_id, pattern in snapshot.employee_patterns.items():
        lines.append(f"  • {pattern.name} ({emp_id})")
        lines.append(f"    - Status: {pattern.current_status}")
        lines.append(f"    - Hours: {pattern.total_hours_logged:.1f} | Tasks: {pattern.total_tasks_completed}")
        lines.append(f"    - Productivity: {pattern.productivity_score:.1f}% | Utilization: {pattern.utilization_rate:.1f}%")
    
    return "\n".join(lines)
