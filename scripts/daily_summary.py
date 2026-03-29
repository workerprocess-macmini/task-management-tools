"""
Automated Daily Summary Generator
Feature 3: Automated Daily Summary

Auto-generates daily summaries by consolidating task data.
Sends summaries to employees with work statistics and insights.
Provides daily digest automation for work tracking system.
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
class TaskSummaryItem:
    """Represents a single task in a daily summary."""
    
    task_id: str = ""
    title: str = ""
    duration_hours: float = 0.0
    category: str = ""
    priority: str = "medium"
    status: str = "completed"  # completed, in_progress, pending
    
    # Optional metadata
    description: str = ""
    tags: List[str] = field(default_factory=list)
    completion_time: Optional[str] = None  # ISO timestamp
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> TaskSummaryItem:
        """Create from dictionary."""
        return TaskSummaryItem(**data)


@dataclass
class CategorySummary:
    """Summary statistics for a work category."""
    
    category: str = ""
    total_hours: float = 0.0
    task_count: int = 0
    percentage_of_day: float = 0.0  # % of total work time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> CategorySummary:
        """Create from dictionary."""
        return CategorySummary(**data)


@dataclass
class DailySummary:
    """Complete daily summary for an employee."""
    
    summary_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str = ""
    employee_name: str = ""
    
    # Date info
    summary_date: str = ""  # YYYY-MM-DD format
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Work statistics
    total_work_hours: float = 0.0
    total_tasks_completed: int = 0
    total_tasks_in_progress: int = 0
    
    # Tasks
    tasks: List[TaskSummaryItem] = field(default_factory=list)
    
    # Category breakdown
    category_summaries: Dict[str, CategorySummary] = field(default_factory=dict)
    
    # Insights & metrics
    productivity_score: float = 0.0  # 0-100
    most_productive_hour: str = ""  # HH:00 format
    longest_task: Optional[TaskSummaryItem] = None
    
    # Top achievements
    top_achievements: List[str] = field(default_factory=list)
    
    # Notes/observations
    observations: str = ""
    recommendations: List[str] = field(default_factory=list)
    
    # Send status
    sent_at: Optional[str] = None
    sent_to_email: Optional[str] = None
    status: str = "generated"  # generated, sent, delivered, failed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        
        # Convert nested objects
        data["tasks"] = [t.to_dict() for t in self.tasks]
        data["category_summaries"] = {
            cat: summary.to_dict()
            for cat, summary in self.category_summaries.items()
        }
        if self.longest_task:
            data["longest_task"] = self.longest_task.to_dict()
        
        return data
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> DailySummary:
        """Create from dictionary."""
        # Reconstruct nested objects
        tasks = [TaskSummaryItem.from_dict(t) for t in data.get("tasks", [])]
        categories = {
            cat: CategorySummary.from_dict(summary)
            for cat, summary in data.get("category_summaries", {}).items()
        }
        longest_task = None
        if data.get("longest_task"):
            longest_task = TaskSummaryItem.from_dict(data["longest_task"])
        
        return DailySummary(
            summary_id=data.get("summary_id", str(uuid.uuid4())),
            employee_id=data.get("employee_id", ""),
            employee_name=data.get("employee_name", ""),
            summary_date=data.get("summary_date", ""),
            generated_at=data.get("generated_at", datetime.now(timezone.utc).isoformat()),
            total_work_hours=data.get("total_work_hours", 0.0),
            total_tasks_completed=data.get("total_tasks_completed", 0),
            total_tasks_in_progress=data.get("total_tasks_in_progress", 0),
            tasks=tasks,
            category_summaries=categories,
            productivity_score=data.get("productivity_score", 0.0),
            most_productive_hour=data.get("most_productive_hour", ""),
            longest_task=longest_task,
            top_achievements=data.get("top_achievements", []),
            observations=data.get("observations", ""),
            recommendations=data.get("recommendations", []),
            sent_at=data.get("sent_at"),
            sent_to_email=data.get("sent_to_email"),
            status=data.get("status", "generated")
        )


class DailySummaryGenerator:
    """Generates and manages daily summaries for employees."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize summary generator.
        
        Args:
            data_dir: Directory for storing summaries. Defaults to ./summaries
        """
        self.data_dir = data_dir or Path("./summaries")
        self.data_dir.mkdir(exist_ok=True, parents=True)
        
        self.summaries: Dict[str, DailySummary] = {}
        self.lock = threading.RLock()
        
        # Load existing summaries
        self._load_summaries()
    
    def _load_summaries(self) -> None:
        """Load all summaries from disk."""
        with self.lock:
            for summary_file in self.data_dir.glob("summary_*.json"):
                try:
                    with open(summary_file, "r") as f:
                        data = json.load(f)
                        summary = DailySummary.from_dict(data)
                        self.summaries[summary.summary_id] = summary
                except (json.JSONDecodeError, ValueError):
                    pass
    
    def generate_summary(
        self,
        employee_id: str,
        employee_name: str,
        summary_date: str,
        tasks: List[Dict[str, Any]]
    ) -> DailySummary:
        """
        Generate a daily summary for an employee.
        
        Args:
            employee_id: Employee ID
            employee_name: Employee name
            summary_date: Summary date (YYYY-MM-DD)
            tasks: List of task data dicts with keys:
                - task_id, title, duration_hours, category, priority, status, completion_time, notes, tags
        
        Returns:
            DailySummary object
        """
        with self.lock:
            summary = DailySummary(
                employee_id=employee_id,
                employee_name=employee_name,
                summary_date=summary_date
            )
            
            # Process tasks
            category_hours: Dict[str, float] = {}
            total_hours = 0.0
            task_items = []
            longest_task = None
            longest_duration = 0.0
            
            for task_data in tasks:
                task_item = TaskSummaryItem(
                    task_id=task_data.get("task_id", ""),
                    title=task_data.get("title", "Untitled"),
                    duration_hours=float(task_data.get("duration_hours", 0.0)),
                    category=task_data.get("category", "other"),
                    priority=task_data.get("priority", "medium"),
                    status=task_data.get("status", "completed"),
                    description=task_data.get("description", ""),
                    tags=task_data.get("tags", []),
                    completion_time=task_data.get("completion_time"),
                    notes=task_data.get("notes", "")
                )
                
                task_items.append(task_item)
                
                # Track by category
                category = task_item.category
                category_hours[category] = category_hours.get(category, 0.0) + task_item.duration_hours
                total_hours += task_item.duration_hours
                
                # Track task counts
                if task_item.status == "completed":
                    summary.total_tasks_completed += 1
                elif task_item.status == "in_progress":
                    summary.total_tasks_in_progress += 1
                
                # Track longest task
                if task_item.duration_hours > longest_duration:
                    longest_duration = task_item.duration_hours
                    longest_task = task_item
            
            summary.tasks = task_items
            summary.total_work_hours = round(total_hours, 2)
            summary.longest_task = longest_task
            
            # Build category summaries
            for category, hours in category_hours.items():
                percentage = (hours / total_hours * 100) if total_hours > 0 else 0.0
                summary.category_summaries[category] = CategorySummary(
                    category=category,
                    total_hours=round(hours, 2),
                    task_count=sum(1 for t in task_items if t.category == category),
                    percentage_of_day=round(percentage, 1)
                )
            
            # Calculate productivity score
            summary.productivity_score = self._calculate_productivity_score(summary)
            
            # Generate insights
            summary.top_achievements = self._generate_achievements(summary)
            summary.observations = self._generate_observations(summary)
            summary.recommendations = self._generate_recommendations(summary)
            summary.most_productive_hour = self._find_peak_hour(summary)
            
            # Store summary
            self.summaries[summary.summary_id] = summary
            self._save_summary(summary)
            
            return summary
    
    def _calculate_productivity_score(self, summary: DailySummary) -> float:
        """
        Calculate productivity score based on work metrics.
        
        Args:
            summary: Daily summary
        
        Returns:
            Productivity score (0-100)
        """
        score = 0.0
        
        # Base: hours worked (target 8 hours = 40 points)
        hours_ratio = min(summary.total_work_hours / 8.0, 1.5)  # Cap at 150%
        score += hours_ratio * 40
        
        # Tasks completed (target 5-6 tasks = 30 points)
        tasks_ratio = min(summary.total_tasks_completed / 6.0, 1.5)
        score += tasks_ratio * 30
        
        # Task diversity (categories covered = 20 points)
        unique_categories = len(summary.category_summaries)
        category_score = min(unique_categories / 4.0, 1.0) * 20
        score += category_score
        
        # In-progress task penalty (incomplete work = -10 points max)
        if summary.total_tasks_in_progress > 0:
            penalty = min(summary.total_tasks_in_progress * 2, 10)
            score -= penalty
        
        # Final score: 0-100 range
        return round(min(max(score, 0.0), 100.0), 1)
    
    def _generate_achievements(self, summary: DailySummary) -> List[str]:
        """Generate top achievements for the summary."""
        achievements = []
        
        # Achievement: Completed multiple tasks
        if summary.total_tasks_completed >= 5:
            achievements.append(f"✅ Completed {summary.total_tasks_completed} tasks today")
        
        # Achievement: Reached target hours
        if summary.total_work_hours >= 8.0:
            achievements.append(f"⏰ Met daily target with {summary.total_work_hours:.1f} hours")
        
        # Achievement: Worked on high priority items
        high_priority_count = sum(1 for t in summary.tasks if t.priority == "high")
        if high_priority_count > 0:
            achievements.append(f"🎯 Completed {high_priority_count} high-priority task(s)")
        
        # Achievement: High productivity score
        if summary.productivity_score >= 80:
            achievements.append(f"🚀 Exceptional productivity ({summary.productivity_score:.0f}%)")
        
        # Achievement: Multiple categories
        if len(summary.category_summaries) >= 3:
            achievements.append(f"🔄 Worked across {len(summary.category_summaries)} categories")
        
        return achievements[:3]  # Top 3 achievements
    
    def _generate_observations(self, summary: DailySummary) -> str:
        """Generate observations about the work day."""
        if summary.total_work_hours == 0:
            return "No work logged for this date."
        
        obs_parts = []
        
        # Most productive category
        if summary.category_summaries:
            top_category = max(
                summary.category_summaries.items(),
                key=lambda x: x[1].total_hours
            )
            obs_parts.append(f"Focus area: {top_category[0]} ({top_category[1].total_hours:.1f}h)")
        
        # Work pace
        if summary.longest_task:
            obs_parts.append(f"Longest task: {summary.longest_task.title} ({summary.longest_task.duration_hours:.1f}h)")
        
        # Completion rate
        if summary.total_tasks_completed + summary.total_tasks_in_progress > 0:
            total_tasks = summary.total_tasks_completed + summary.total_tasks_in_progress
            completion_rate = (summary.total_tasks_completed / total_tasks) * 100
            obs_parts.append(f"Completion rate: {completion_rate:.0f}%")
        
        return " | ".join(obs_parts) if obs_parts else "Work day summary complete."
    
    def _generate_recommendations(self, summary: DailySummary) -> List[str]:
        """Generate recommendations based on work patterns."""
        recommendations = []
        
        # Recommendation: Increase hours if below target
        if summary.total_work_hours < 6.0:
            recommendations.append("Try to log more work time tomorrow")
        
        # Recommendation: Complete pending tasks
        if summary.total_tasks_in_progress > 0:
            recommendations.append(f"Complete {summary.total_tasks_in_progress} task(s) in progress")
        
        # Recommendation: Balance work categories
        if len(summary.category_summaries) < 2:
            recommendations.append("Consider diversifying work across categories")
        
        # Recommendation: Take breaks
        if summary.total_work_hours > 10:
            recommendations.append("Remember to take breaks and rest")
        
        # Recommendation: Focus on high priority
        high_priority = sum(1 for t in summary.tasks if t.priority == "high")
        if high_priority == 0 and summary.tasks:
            recommendations.append("Consider prioritizing high-impact tasks tomorrow")
        
        return recommendations[:2]  # Top 2 recommendations
    
    def _find_peak_hour(self, summary: DailySummary) -> str:
        """Find the hour with the most tasks completed."""
        if not summary.tasks:
            return ""
        
        hour_counts: Dict[str, int] = {}
        for task in summary.tasks:
            if task.completion_time:
                try:
                    # Extract hour from completion_time (ISO format)
                    hour = task.completion_time.split("T")[1][:2]
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1
                except (IndexError, AttributeError):
                    pass
        
        if hour_counts:
            peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
            return f"{peak_hour}:00"
        
        return ""
    
    def _save_summary(self, summary: DailySummary) -> Path:
        """Save summary to disk."""
        summary_path = self.data_dir / f"summary_{summary.summary_id}.json"
        with open(summary_path, "w") as f:
            json.dump(summary.to_dict(), f, indent=2)
        return summary_path
    
    def get_summary(self, summary_id: str) -> Optional[DailySummary]:
        """Get a specific summary by ID."""
        with self.lock:
            return self.summaries.get(summary_id)
    
    def get_employee_summaries(
        self,
        employee_id: str,
        days: int = 7
    ) -> List[DailySummary]:
        """
        Get summaries for an employee over last N days.
        
        Args:
            employee_id: Employee ID
            days: Number of days to retrieve
        
        Returns:
            List of summaries sorted by date (newest first)
        """
        with self.lock:
            employee_summaries = [
                s for s in self.summaries.values()
                if s.employee_id == employee_id
            ]
            
            # Sort by date (newest first)
            employee_summaries.sort(key=lambda s: s.summary_date, reverse=True)
            
            return employee_summaries[:days]
    
    def list_summaries(
        self,
        summary_date: Optional[str] = None,
        limit: int = 50
    ) -> List[DailySummary]:
        """
        List summaries with optional filtering.
        
        Args:
            summary_date: Filter by specific date (YYYY-MM-DD)
            limit: Maximum number to return
        
        Returns:
            List of summaries sorted by generated_at (newest first)
        """
        with self.lock:
            summaries = list(self.summaries.values())
            
            if summary_date:
                summaries = [s for s in summaries if s.summary_date == summary_date]
            
            # Sort by generated time (newest first)
            summaries.sort(key=lambda s: s.generated_at, reverse=True)
            
            return summaries[:limit]
    
    def mark_summary_sent(
        self,
        summary_id: str,
        email: Optional[str] = None
    ) -> bool:
        """
        Mark a summary as sent.
        
        Args:
            summary_id: Summary ID
            email: Email address sent to
        
        Returns:
            True if successful
        """
        with self.lock:
            summary = self.summaries.get(summary_id)
            if not summary:
                return False
            
            summary.status = "sent"
            summary.sent_at = datetime.now(timezone.utc).isoformat()
            if email:
                summary.sent_to_email = email
            
            self._save_summary(summary)
            return True
    
    def mark_summary_delivered(self, summary_id: str) -> bool:
        """
        Mark a summary as delivered.
        
        Args:
            summary_id: Summary ID
        
        Returns:
            True if successful
        """
        with self.lock:
            summary = self.summaries.get(summary_id)
            if not summary:
                return False
            
            summary.status = "delivered"
            self._save_summary(summary)
            return True
    
    def mark_summary_failed(self, summary_id: str, reason: str = "") -> bool:
        """
        Mark a summary send as failed.
        
        Args:
            summary_id: Summary ID
            reason: Failure reason
        
        Returns:
            True if successful
        """
        with self.lock:
            summary = self.summaries.get(summary_id)
            if not summary:
                return False
            
            summary.status = "failed"
            if reason:
                summary.observations = f"Send failed: {reason}"
            
            self._save_summary(summary)
            return True


def format_summary_email(summary: DailySummary) -> str:
    """
    Format daily summary as email-ready text.
    
    Args:
        summary: Daily summary
    
    Returns:
        Formatted email text
    """
    lines = [
        f"=== Daily Summary for {summary.summary_date} ===",
        f"",
        f"Hello {summary.employee_name},",
        f"",
        f"Here's your work summary for {summary.summary_date}:",
        f"",
        f"📊 WORK STATISTICS",
        f"Total Hours: {summary.total_work_hours:.1f}h | Tasks Completed: {summary.total_tasks_completed}",
        f"Productivity Score: {summary.productivity_score:.0f}% | Peak Hour: {summary.most_productive_hour or 'N/A'}",
        f"",
        f"🎯 TOP ACHIEVEMENTS",
    ]
    
    for achievement in summary.top_achievements:
        lines.append(f"  {achievement}")
    
    if not summary.top_achievements:
        lines.append("  Keep up the good work!")
    
    lines.extend([
        f"",
        f"📈 CATEGORY BREAKDOWN",
    ])
    
    for category, cat_summary in summary.category_summaries.items():
        lines.append(f"  • {category}: {cat_summary.total_hours:.1f}h ({cat_summary.percentage_of_day:.0f}%)")
    
    if summary.longest_task:
        lines.extend([
            f"",
            f"⏱️ LONGEST TASK",
            f"  {summary.longest_task.title}: {summary.longest_task.duration_hours:.1f} hours",
        ])
    
    if summary.observations:
        lines.extend([
            f"",
            f"📝 OBSERVATIONS",
            f"  {summary.observations}",
        ])
    
    if summary.recommendations:
        lines.extend([
            f"",
            f"💡 RECOMMENDATIONS",
        ])
        for rec in summary.recommendations:
            lines.append(f"  • {rec}")
    
    lines.extend([
        f"",
        f"Generated: {summary.generated_at}",
        f"",
        f"---",
        f"This is an automated summary from your work tracking system.",
    ])
    
    return "\n".join(lines)
