"""
Insights Generators Module for Work Logging System
Generates actionable insights and recommendations from work data.

Feature 4: Productivity Insights - Insight Generation Engine
Phase 2 Enhancement: Auto-collect metrics from work logs
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from statistics import mean, median, stdev

from productivity_analyzer import (
    ProductivityAnalyzer, ProductivityMetric, WorkPattern,
    ProductivityInsight, ProductivityReport
)


class InsightsGenerator:
    """
    Generates actionable productivity insights from work data.
    
    Analyzes metrics and patterns to create insights about:
    - Work habits and patterns
    - Productivity trends
    - Focus and balance
    - Opportunities for improvement
    """
    
    def __init__(self, analyzer: ProductivityAnalyzer):
        """
        Initialize the insights generator.
        
        Args:
            analyzer: ProductivityAnalyzer instance
        """
        self.analyzer = analyzer
    
    def generate_daily_insight(
        self,
        employee_id: str,
        daily_metrics: Dict[str, float],
        daily_summary: Optional[Dict[str, Any]] = None
    ) -> Optional[ProductivityInsight]:
        """
        Generate a single daily productivity insight.
        
        Args:
            employee_id: The employee ID
            daily_metrics: Dictionary of metric values for the day
            daily_summary: Optional daily summary data
            
        Returns:
            A ProductivityInsight or None if insufficient data
        """
        if not daily_metrics or not employee_id:
            return None
        
        # Determine insight based on metrics
        tasks_completed = daily_metrics.get("tasks_completed", 0)
        focus_score = daily_metrics.get("focus_score", 0)
        hours_worked = daily_metrics.get("hours_worked", 0)
        
        # Default insight if no metrics
        if not any(daily_metrics.values()):
            return None
        
        # Analyze focus score
        if focus_score >= 80:
            insight_type = "strength"
            title = "Strong Focus Today"
            description = "High focus score indicates productive, concentrated work."
            action = "Maintain current work environment and focus practices."
        elif focus_score >= 60:
            insight_type = "pattern"
            title = "Moderate Focus Detected"
            description = "Focus was moderate - some distractions present."
            action = "Consider reducing interruptions or context switches."
        else:
            insight_type = "weakness"
            title = "Low Focus Levels"
            description = "Multiple interruptions and context switches detected."
            action = "Block focused work time, minimize meetings, silence notifications."
        
        insight = ProductivityInsight(
            employee_id=employee_id,
            title=title,
            description=description,
            insight_type=insight_type,
            severity="info" if insight_type == "strength" else "medium",
            confidence=0.85,
            recommended_action=action,
            action_category="focus",
            potential_impact="Medium",
            impact_area="Productivity",
            analysis_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            tags=["daily", "focus"]
        )
        
        return insight
    
    def generate_trend_insights(
        self,
        employee_id: str,
        historical_metrics: List[ProductivityMetric],
        period_days: int = 7
    ) -> List[ProductivityInsight]:
        """
        Generate insights about productivity trends.
        
        Args:
            employee_id: The employee ID
            historical_metrics: List of historical metrics
            period_days: Number of days to analyze
            
        Returns:
            List of trend insights
        """
        insights: List[ProductivityInsight] = []
        
        if not historical_metrics or len(historical_metrics) < 3:
            return insights
        
        # Group metrics by type
        metrics_by_type: Dict[str, List[float]] = {}
        for metric in historical_metrics:
            if metric.metric_name not in metrics_by_type:
                metrics_by_type[metric.metric_name] = []
            metrics_by_type[metric.metric_name].append(metric.value)
        
        # Analyze trends for each metric type
        for metric_name, values in metrics_by_type.items():
            if len(values) < 3:
                continue
            
            # Calculate trend (simple: compare first third to last third)
            third = len(values) // 3
            early_avg = mean(values[:third]) if third > 0 else values[0]
            late_avg = mean(values[-third:]) if third > 0 else values[-1]
            
            trend_pct = ((late_avg - early_avg) / early_avg * 100) if early_avg > 0 else 0
            
            # Generate insight based on trend
            if abs(trend_pct) < 5:
                continue  # No significant trend
            
            if trend_pct > 10:
                insight = ProductivityInsight(
                    employee_id=employee_id,
                    title=f"Improving {metric_name.replace('_', ' ')}",
                    description=f"Your {metric_name.replace('_', ' ')} has improved by {trend_pct:.1f}% over the past {period_days} days.",
                    insight_type="strength",
                    severity="info",
                    confidence=0.8,
                    recommended_action="Continue current practices - they are working well.",
                    action_category="optimization",
                    potential_impact="High",
                    impact_area="Productivity",
                    analysis_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    tags=["trend", "positive", metric_name]
                )
            elif trend_pct < -10:
                insight = ProductivityInsight(
                    employee_id=employee_id,
                    title=f"Declining {metric_name.replace('_', ' ')}",
                    description=f"Your {metric_name.replace('_', ' ')} has declined by {abs(trend_pct):.1f}% over the past {period_days} days.",
                    insight_type="weakness",
                    severity="medium",
                    confidence=0.8,
                    recommended_action="Investigate recent changes - take corrective action.",
                    action_category="improvement",
                    potential_impact="High",
                    impact_area="Productivity",
                    analysis_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    tags=["trend", "negative", metric_name]
                )
            else:
                continue
            
            insights.append(insight)
        
        return insights
    
    def generate_work_balance_insights(
        self,
        employee_id: str,
        daily_summaries: List[Dict[str, Any]]
    ) -> List[ProductivityInsight]:
        """
        Generate insights about work-life balance and workload.
        
        Args:
            employee_id: The employee ID
            daily_summaries: List of daily summary data
            
        Returns:
            List of balance insights
        """
        insights: List[ProductivityInsight] = []
        
        if not daily_summaries or len(daily_summaries) < 3:
            return insights
        
        # Calculate statistics
        hours_per_day = [s.get("total_work_hours", 0) for s in daily_summaries]
        weekend_days = sum(1 for s in daily_summaries if s.get("is_weekend", False))
        
        avg_hours = mean(hours_per_day)
        max_hours = max(hours_per_day)
        
        # Check for overwork
        if avg_hours > 9:
            insights.append(ProductivityInsight(
                employee_id=employee_id,
                title="High Workload Alert",
                description=f"Average of {avg_hours:.1f} hours/day exceeds standard 8-hour workday.",
                insight_type="weakness",
                severity="high",
                confidence=0.9,
                recommended_action="Redistribute work, take time off, or delegate tasks to prevent burnout.",
                action_category="workload",
                potential_impact="High",
                impact_area="Health",
                analysis_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                tags=["workload", "health", "balance"]
            ))
        
        # Check for weekend work
        if weekend_days > 0:
            insights.append(ProductivityInsight(
                employee_id=employee_id,
                title="Weekend Work Detected",
                description=f"Work activity detected on {weekend_days} weekend days.",
                insight_type="weakness",
                severity="medium",
                confidence=0.95,
                recommended_action="Ensure adequate rest days. Maintain work-life balance.",
                action_category="workload",
                potential_impact="Medium",
                impact_area="Health",
                analysis_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                tags=["weekend", "health", "balance"]
            ))
        
        # Check for consistency
        if len(hours_per_day) >= 5:
            try:
                std_dev = stdev(hours_per_day)
                if std_dev < 1.5:
                    insights.append(ProductivityInsight(
                        employee_id=employee_id,
                        title="Consistent Work Schedule",
                        description="Your work schedule is very consistent, which aids planning and productivity.",
                        insight_type="strength",
                        severity="info",
                        confidence=0.85,
                        recommended_action="Maintain this consistency - predictable patterns improve focus.",
                        action_category="time_management",
                        potential_impact="Medium",
                        impact_area="Productivity",
                        analysis_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                        tags=["consistency", "schedule"]
                    ))
            except ValueError:
                pass
        
        return insights
    
    def generate_focus_insights(
        self,
        employee_id: str,
        session_data: List[Dict[str, Any]]
    ) -> List[ProductivityInsight]:
        """
        Generate insights about focus patterns and interruptions.
        
        Args:
            employee_id: The employee ID
            session_data: List of work session data
            
        Returns:
            List of focus insights
        """
        insights: List[ProductivityInsight] = []
        
        if not session_data or len(session_data) < 3:
            return insights
        
        # Calculate focus metrics
        total_sessions = len(session_data)
        avg_session_length = mean(s.get("duration_minutes", 0) for s in session_data)
        pause_count = sum(s.get("pause_count", 0) for s in session_data)
        context_switches = total_sessions  # Simple proxy
        
        # Analyze session length
        if avg_session_length > 60:
            insights.append(ProductivityInsight(
                employee_id=employee_id,
                title="Long Focus Sessions",
                description=f"Average session length of {avg_session_length:.0f} minutes shows good focus ability.",
                insight_type="strength",
                severity="info",
                confidence=0.8,
                recommended_action="Maintain these long, uninterrupted work blocks.",
                action_category="focus",
                potential_impact="High",
                impact_area="Productivity",
                analysis_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                tags=["focus", "deep_work"]
            ))
        elif avg_session_length < 30:
            insights.append(ProductivityInsight(
                employee_id=employee_id,
                title="Frequent Context Switches",
                description=f"Short sessions ({avg_session_length:.0f} min avg) indicate frequent interruptions.",
                insight_type="weakness",
                severity="medium",
                confidence=0.75,
                recommended_action="Block time for focused work. Batch similar tasks together.",
                action_category="focus",
                potential_impact="High",
                impact_area="Productivity",
                analysis_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                tags=["focus", "interruptions"]
            ))
        
        # Analyze break patterns
        if pause_count > 0 and total_sessions > 0:
            avg_pauses = pause_count / total_sessions
            if avg_pauses > 3:
                insights.append(ProductivityInsight(
                    employee_id=employee_id,
                    title="Frequent Breaks Detected",
                    description=f"Average of {avg_pauses:.1f} breaks per session may impact flow state.",
                    insight_type="opportunity",
                    severity="low",
                    confidence=0.7,
                    recommended_action="Consider consolidating breaks to maintain focus flow.",
                    action_category="focus",
                    potential_impact="Medium",
                    impact_area="Productivity",
                    analysis_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    tags=["breaks", "focus"]
                ))
            elif avg_pauses > 0:
                insights.append(ProductivityInsight(
                    employee_id=employee_id,
                    title="Healthy Break Pattern",
                    description="Your break frequency is balanced - maintaining focus without overexertion.",
                    insight_type="strength",
                    severity="info",
                    confidence=0.8,
                    recommended_action="Continue current break practices.",
                    action_category="health",
                    potential_impact="Medium",
                    impact_area="Health",
                    analysis_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    tags=["breaks", "health"]
                ))
        
        return insights
    
    def generate_category_insights(
        self,
        employee_id: str,
        category_distribution: Dict[str, float]
    ) -> List[ProductivityInsight]:
        """
        Generate insights about work category distribution.
        
        Args:
            employee_id: The employee ID
            category_distribution: Dictionary of category to percentage
            
        Returns:
            List of category insights
        """
        insights: List[ProductivityInsight] = []
        
        if not category_distribution:
            return insights
        
        # Find dominant category
        if category_distribution:
            dominant = max(category_distribution.items(), key=lambda x: x[1])
            category_name = dominant[0]
            percentage = dominant[1]
            
            if percentage > 70:
                insights.append(ProductivityInsight(
                    employee_id=employee_id,
                    title=f"Heavy {category_name.capitalize()} Focus",
                    description=f"{percentage:.0f}% of work time spent on {category_name}.",
                    insight_type="pattern",
                    severity="info",
                    confidence=0.9,
                    recommended_action="Ensure diverse work tasks to avoid specialization bottleneck.",
                    action_category="workload",
                    potential_impact="Medium",
                    impact_area="Productivity",
                    analysis_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    tags=["category", category_name]
                ))
        
        # Check for balanced distribution
        if len(category_distribution) >= 3:
            max_pct = max(category_distribution.values())
            min_pct = min(category_distribution.values())
            if max_pct - min_pct < 20:
                insights.append(ProductivityInsight(
                    employee_id=employee_id,
                    title="Well-Balanced Work Distribution",
                    description="Work is evenly distributed across multiple categories.",
                    insight_type="strength",
                    severity="info",
                    confidence=0.85,
                    recommended_action="Maintain this balanced approach to build diverse skills.",
                    action_category="workload",
                    potential_impact="Medium",
                    impact_area="Productivity",
                    analysis_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    tags=["balance", "distribution"]
                ))
        
        return insights


class RecommendationsGenerator:
    """
    Generates actionable recommendations from insights.
    """
    
    @staticmethod
    def generate_recommendations(insights: List[ProductivityInsight]) -> List[str]:
        """
        Generate actionable recommendations from insights.
        
        Args:
            insights: List of insights
            
        Returns:
            List of recommendations
        """
        recommendations: List[str] = []
        seen_actions = set()
        
        # Sort by confidence and severity
        sorted_insights = sorted(
            insights,
            key=lambda i: (i.confidence, 1 if i.severity == "high" else 0),
            reverse=True
        )
        
        # Generate recommendations from top insights
        for insight in sorted_insights[:5]:  # Top 5 insights
            if insight.recommended_action and insight.recommended_action not in seen_actions:
                recommendations.append(insight.recommended_action)
                seen_actions.add(insight.recommended_action)
        
        return recommendations
    
    @staticmethod
    def prioritize_actions(insights: List[ProductivityInsight]) -> List[Dict[str, Any]]:
        """
        Prioritize actions based on impact and feasibility.
        
        Args:
            insights: List of insights
            
        Returns:
            Prioritized list of action dictionaries
        """
        actions: List[Dict[str, Any]] = []
        
        for insight in insights:
            if insight.recommended_action:
                priority = 1  # Default
                if insight.severity in ["high", "critical"]:
                    priority = 1
                elif insight.severity == "medium":
                    priority = 2
                else:
                    priority = 3
                
                action = {
                    "action": insight.recommended_action,
                    "category": insight.action_category,
                    "priority": priority,
                    "impact": insight.potential_impact,
                    "supported_by": insight.insight_id,
                    "confidence": insight.confidence
                }
                actions.append(action)
        
        # Sort by priority
        return sorted(actions, key=lambda a: a["priority"])


def calculate_focus_score(
    interruptions: int = 0,
    context_switches: int = 0,
    deep_work_hours: float = 0,
    total_hours: float = 8
) -> float:
    """
    Calculate focus score based on work metrics.
    
    Args:
        interruptions: Number of interruptions during the day
        context_switches: Number of context switches
        deep_work_hours: Hours spent in deep, focused work
        total_hours: Total hours worked
        
    Returns:
        Focus score (0-100)
    """
    # Base score starts at 100
    score = 100.0
    
    # Deduct for interruptions (max -20)
    interruption_penalty = min(20, interruptions * 2)
    score -= interruption_penalty
    
    # Deduct for context switches (max -30)
    switch_penalty = min(30, context_switches * 1.5)
    score -= switch_penalty
    
    # Add bonus for deep work (max +20)
    if total_hours > 0:
        deep_work_ratio = deep_work_hours / total_hours
        deep_work_bonus = min(20, deep_work_ratio * 30)
        score += deep_work_bonus
    
    # Ensure score is between 0-100
    return max(0, min(100, score))


def analyze_daily_logs(
    employee_id: str,
    date: str
) -> Dict[str, Any]:
    """
    Analyze work logs for a specific employee and date.
    
    Reads work logs from ../../../logs/{date}/{employee_id}.json
    Parses Phase 1 log format and extracts metrics:
    - interruptions: count of events
    - context_switches: number of task transitions
    - deep_work_hours: 80% of total duration
    - total_hours: sum of all task durations
    - focus_score: calculated from metrics
    
    Phase 1 Log Format:
    [
      {
        "task_id": "...",
        "timestamp": "2026-03-28 15:57:56",
        "timestamp_unix": 1774688276,
        "employee_id": "8557772399",
        "project": "Open Call",
        "status": "START",
        "current_status": "DONE",
        "subject": "งาน",
        "message": "...",
        "events": [
          {
            "timestamp": "2026-03-28 16:30:51",
            "timestamp_unix": 1774690251,
            "status": "DONE",
            "message": "เสร็จแล้ว"
          }
        ],
        "last_timestamp": "2026-03-28 16:30:51",
        "last_timestamp_unix": 1774690251
      }
    ]
    
    Args:
        employee_id: Employee ID (e.g., "8557772399")
        date: Date in YYYY-MM-DD format (e.g., "2026-03-28")
        
    Returns:
        Dictionary with extracted metrics:
        {
            "interruptions": int (count of events per task),
            "context_switches": int (number of task transitions),
            "deep_work_hours": float (80% of duration),
            "total_hours": float (sum of all task durations),
            "focus_score": float (0-100),
            "task_count": int (number of tasks),
            "duration_minutes": float (total duration in minutes),
            "categories": dict (project distribution),
            "log_file": str (path to log file),
            "log_exists": bool
        }
    """
    # Build path to logs
    # From work-logging/scripts -> ../../../logs
    script_dir = Path(__file__).parent
    logs_dir = script_dir / "../../../logs" / date / f"{employee_id}.json"
    logs_path = logs_dir.resolve()
    
    metrics = {
        "interruptions": 0,
        "context_switches": 0,
        "deep_work_hours": 0.0,
        "total_hours": 0.0,
        "duration_minutes": 0.0,
        "focus_score": 0.0,
        "task_count": 0,
        "categories": {},
        "log_file": str(logs_path),
        "log_exists": False
    }
    
    # Check if log file exists
    if not logs_path.exists():
        print(f"Warning: Log file not found at {logs_path}", file=sys.stderr)
        return metrics
    
    metrics["log_exists"] = True
    
    try:
        with open(logs_path, 'r') as f:
            logs = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading log file: {e}", file=sys.stderr)
        return metrics
    
    if not logs or not isinstance(logs, list):
        print(f"Warning: No valid logs found in {logs_path}", file=sys.stderr)
        return metrics
    
    # Extract metrics from Phase 1 logs
    task_count = len(logs)
    metrics["task_count"] = task_count
    
    # Calculate metrics from all tasks
    total_duration_minutes = 0.0
    total_interruptions = 0
    project_counts = {}
    
    for task in logs:
        if not isinstance(task, dict):
            continue
        
        # Count projects/categories
        project = task.get("project", "uncategorized")
        project_counts[project] = project_counts.get(project, 0) + 1
        
        # Calculate duration from timestamp to last_timestamp
        # Phase 1 format has unix timestamps
        if "timestamp_unix" in task and "last_timestamp_unix" in task:
            start_unix = task.get("timestamp_unix", 0)
            end_unix = task.get("last_timestamp_unix", 0)
            
            if end_unix >= start_unix:
                duration_seconds = end_unix - start_unix
                duration_minutes = duration_seconds / 60
                total_duration_minutes += duration_minutes
        
        # Count interruptions from events
        # Each event represents an update/interruption
        events = task.get("events", [])
        if isinstance(events, list):
            # Count events as interruptions
            # If there are events, they indicate interruptions during the task
            interruptions_for_task = len(events)
            total_interruptions += interruptions_for_task
    
    # Calculate total hours from minutes
    metrics["duration_minutes"] = total_duration_minutes
    metrics["total_hours"] = total_duration_minutes / 60.0
    
    # Context switches: number of task transitions
    # If we have N tasks, we have at most N-1 context switches
    if task_count > 1:
        metrics["context_switches"] = task_count - 1
    else:
        metrics["context_switches"] = 0
    
    # Interruptions: sum of all events across all tasks
    metrics["interruptions"] = total_interruptions
    
    # Deep work minutes: 80% of total duration (reasonable estimate)
    # Deep work is work without interruptions
    metrics["deep_work_hours"] = (total_duration_minutes * 0.8) / 60.0
    
    # Store project/category distribution
    if project_counts:
        total = sum(project_counts.values())
        metrics["categories"] = {
            proj: (count / total * 100) for proj, count in project_counts.items()
        }
    
    # Calculate focus score
    metrics["focus_score"] = calculate_focus_score(
        interruptions=metrics["interruptions"],
        context_switches=metrics["context_switches"],
        deep_work_hours=metrics["deep_work_hours"],
        total_hours=max(1, metrics["total_hours"])  # Avoid division by zero
    )
    
    return metrics


def main():
    """
    Main entry point for insights generator.
    
    Supports three modes:
    1. Auto-collect from logs: --employee-id ID --date YYYY-MM-DD
    2. Direct metrics input: --employee-id ID --metrics SCORE
    3. Raw data input: --employee-id ID --interruptions N --context-switches N --deep-work-hours H
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate productivity insights from work logs or metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-collect from logs (recommended)
  python insights_generators.py --employee-id 8557772399 --date 2026-03-28
  
  # Direct score input
  python insights_generators.py --employee-id 8557772399 --metrics 75
  
  # Raw metrics input
  python insights_generators.py --employee-id 8557772399 --interruptions 3 --context-switches 8 --deep-work-hours 4
        """
    )
    
    parser.add_argument(
        "--employee-id",
        required=True,
        help="Employee ID (e.g., 8557772399)"
    )
    
    parser.add_argument(
        "--date",
        help="Date for log analysis (YYYY-MM-DD format, e.g., 2026-03-28)"
    )
    
    parser.add_argument(
        "--metrics",
        type=float,
        help="Direct focus score input (0-100)"
    )
    
    parser.add_argument(
        "--interruptions",
        type=int,
        default=0,
        help="Number of interruptions"
    )
    
    parser.add_argument(
        "--context-switches",
        type=int,
        default=0,
        help="Number of context switches"
    )
    
    parser.add_argument(
        "--deep-work-hours",
        type=float,
        default=0,
        help="Hours spent in deep work"
    )
    
    parser.add_argument(
        "--output-json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    employee_id = args.employee_id
    focus_score = None
    extracted_metrics = None
    
    # Determine which mode to use
    if args.date:
        # Mode 1: Auto-collect from logs (preferred)
        print(f"🔍 Analyzing work logs for {employee_id} on {args.date}...", file=sys.stderr)
        extracted_metrics = analyze_daily_logs(employee_id, args.date)
        focus_score = extracted_metrics["focus_score"]
        
        print(f"\n📊 Extracted Metrics:", file=sys.stderr)
        print(f"  Total Hours: {extracted_metrics['total_hours']:.2f}h", file=sys.stderr)
        print(f"  Tasks: {extracted_metrics['task_count']}", file=sys.stderr)
        print(f"  Interruptions: {extracted_metrics['interruptions']}", file=sys.stderr)
        print(f"  Context Switches: {extracted_metrics['context_switches']}", file=sys.stderr)
        print(f"  Deep Work Hours: {extracted_metrics['deep_work_hours']:.2f}h", file=sys.stderr)
        print(f"  Categories: {extracted_metrics['categories']}", file=sys.stderr)
        
    elif args.metrics is not None:
        # Mode 2: Direct score input
        focus_score = args.metrics
        print(f"✅ Using provided metrics score: {focus_score}", file=sys.stderr)
        
    else:
        # Mode 3: Raw data input
        focus_score = calculate_focus_score(
            interruptions=args.interruptions,
            context_switches=args.context_switches,
            deep_work_hours=args.deep_work_hours,
            total_hours=8  # Assume standard 8-hour day
        )
        extracted_metrics = {
            "interruptions": args.interruptions,
            "context_switches": args.context_switches,
            "deep_work_hours": args.deep_work_hours,
            "total_hours": 8,
            "focus_score": focus_score,
            "task_count": 5,  # Default estimate
            "categories": {}
        }
        print(f"📊 Calculated focus score from raw metrics: {focus_score:.1f}", file=sys.stderr)
    
    # Generate insights
    print(f"\n✨ Generating insights for focus score: {focus_score:.1f}", file=sys.stderr)
    
    # Create sample metrics for insight generation
    daily_metrics = {
        "focus_score": focus_score,
        "tasks_completed": extracted_metrics["task_count"] if extracted_metrics else 5,
        "hours_worked": extracted_metrics["total_hours"] if extracted_metrics else 8
    }
    
    # Generate insights using the existing InsightsGenerator
    temp_analyzer = ProductivityAnalyzer(str(Path.home()))
    generator = InsightsGenerator(temp_analyzer)
    
    insight = generator.generate_daily_insight(employee_id, daily_metrics)
    
    # Prepare output
    output = {
        "employee_id": employee_id,
        "date": args.date or datetime.now().strftime("%Y-%m-%d"),
        "focus_score": focus_score,
        "metrics": extracted_metrics if extracted_metrics else {
            "interruptions": args.interruptions,
            "context_switches": args.context_switches,
            "deep_work_hours": args.deep_work_hours,
            "total_hours": 8
        },
        "insight": {
            "title": insight.title if insight else "No insight generated",
            "description": insight.description if insight else "",
            "type": insight.insight_type if insight else "unknown",
            "action": insight.recommended_action if insight else ""
        }
    }
    
    if args.output_json:
        print(json.dumps(output, indent=2))
    else:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"📈 PRODUCTIVITY INSIGHT", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        print(f"Employee: {employee_id}", file=sys.stderr)
        print(f"Date: {output['date']}", file=sys.stderr)
        print(f"Focus Score: {focus_score:.1f}/100", file=sys.stderr)
        print(f"\n💡 {insight.title if insight else 'No insight'}", file=sys.stderr)
        if insight:
            print(f"   {insight.description}", file=sys.stderr)
            print(f"\n📋 Recommended Action:", file=sys.stderr)
            print(f"   {insight.recommended_action}", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        
        # Also output JSON for programmatic use
        print(json.dumps(output, indent=2))
    
    return output


if __name__ == "__main__":
    main()
