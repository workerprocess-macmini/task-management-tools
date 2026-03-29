"""
Time Tracking Module for Work Logging System
Handles start/stop/pause/resume of work sessions with timezone support.

Feature 1: Time Tracking & Duration
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
class TimeSession:
    """Represents a single work session with start, stop, and pause tracking."""
    
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""  # Link to work task
    employee_id: str = ""
    project: str = ""
    
    # Timestamps (ISO 8601 with timezone)
    start_time: str = ""  # ISO format: "2026-03-28T10:30:00+07:00"
    end_time: Optional[str] = None  # Set when session ends
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Duration tracking (in seconds)
    total_duration_seconds: int = 0  # Total time (excluding pauses)
    pauses: List[Dict[str, Any]] = field(default_factory=list)  # List of pause periods
    
    # State tracking
    is_active: bool = True  # Session still running
    is_paused: bool = False  # Currently paused
    pause_start: Optional[str] = None  # When current pause started
    
    # Metadata
    category: str = "other"  # development, testing, devops, etc.
    priority: str = "medium"  # low, medium, high, critical
    notes: str = ""
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for JSON serialization."""
        data = asdict(self)
        # Remove field factory defaults that are empty
        return data
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> TimeSession:
        """Create TimeSession from dictionary."""
        return TimeSession(**data)


class TimeTracker:
    """Thread-safe time tracking system for work sessions."""
    
    def __init__(self, tz_offset: str = "+07:00"):
        """
        Initialize tracker.
        
        Args:
            tz_offset: Timezone offset (e.g., "+07:00" for Bangkok)
        """
        self.tz_offset = tz_offset
        self.sessions: Dict[str, TimeSession] = {}  # session_id -> TimeSession
        self.lock = threading.RLock()
        self.auto_pause_threshold = 300  # 5 minutes of inactivity = auto-pause
    
    def _now_iso(self) -> str:
        """Get current timestamp in ISO 8601 format with timezone."""
        dt = datetime.now(timezone.utc)
        # Format with explicit timezone offset
        iso_str = dt.isoformat()
        # Replace +00:00 with configured offset
        return iso_str.replace("+00:00", self.tz_offset)
    
    def _parse_iso(self, iso_str: str) -> datetime:
        """Parse ISO 8601 string to datetime."""
        # Remove timezone info for parsing
        if "+" in iso_str:
            iso_str = iso_str.split("+")[0]
        elif iso_str.endswith("Z"):
            iso_str = iso_str[:-1]
        return datetime.fromisoformat(iso_str)
    
    def start_session(
        self,
        employee_id: str,
        project: str,
        task_id: str,
        category: str = "other",
        priority: str = "medium",
        notes: str = ""
    ) -> TimeSession:
        """
        Start a new tracking session.
        
        Args:
            employee_id: Employee identifier
            project: Project name
            task_id: Link to task ID
            category: Task category
            priority: Task priority
            notes: Optional session notes
        
        Returns:
            TimeSession object
        
        Raises:
            ValueError: If parameters are invalid
        """
        if not employee_id or not project or not task_id:
            raise ValueError("employee_id, project, and task_id are required")
        
        if category not in ["development", "testing", "devops", "management", "communication", "other"]:
            raise ValueError(f"Invalid category: {category}")
        
        if priority not in ["low", "medium", "high", "critical"]:
            raise ValueError(f"Invalid priority: {priority}")
        
        with self.lock:
            session = TimeSession(
                task_id=task_id,
                employee_id=employee_id,
                project=project,
                start_time=self._now_iso(),
                category=category,
                priority=priority,
                notes=notes,
                is_active=True,
                is_paused=False,
            )
            self.sessions[session.session_id] = session
            return session
    
    def pause_session(self, session_id: str) -> TimeSession:
        """
        Pause an active session.
        
        Args:
            session_id: Session to pause
        
        Returns:
            Updated TimeSession
        
        Raises:
            ValueError: If session not found or not active
        """
        with self.lock:
            if session_id not in self.sessions:
                raise ValueError(f"Session not found: {session_id}")
            
            session = self.sessions[session_id]
            
            if not session.is_active:
                raise ValueError(f"Session is not active: {session_id}")
            
            if session.is_paused:
                raise ValueError(f"Session is already paused: {session_id}")
            
            session.is_paused = True
            session.pause_start = self._now_iso()
            return session
    
    def resume_session(self, session_id: str) -> TimeSession:
        """
        Resume a paused session.
        
        Args:
            session_id: Session to resume
        
        Returns:
            Updated TimeSession
        
        Raises:
            ValueError: If session not found or not paused
        """
        with self.lock:
            if session_id not in self.sessions:
                raise ValueError(f"Session not found: {session_id}")
            
            session = self.sessions[session_id]
            
            if not session.is_active:
                raise ValueError(f"Session is not active: {session_id}")
            
            if not session.is_paused:
                raise ValueError(f"Session is not paused: {session_id}")
            
            # Record pause duration
            if session.pause_start:
                pause_end = self._now_iso()
                pause_duration = int(
                    (self._parse_iso(pause_end) - self._parse_iso(session.pause_start)).total_seconds()
                )
                session.pauses.append({
                    "pause_start": session.pause_start,
                    "pause_end": pause_end,
                    "duration_seconds": pause_duration,
                })
            
            session.is_paused = False
            session.pause_start = None
            return session
    
    def stop_session(self, session_id: str) -> TimeSession:
        """
        Stop a session and calculate final duration.
        
        Args:
            session_id: Session to stop
        
        Returns:
            Completed TimeSession with duration_seconds calculated
        
        Raises:
            ValueError: If session not found or already stopped
        """
        with self.lock:
            if session_id not in self.sessions:
                raise ValueError(f"Session not found: {session_id}")
            
            session = self.sessions[session_id]
            
            if not session.is_active:
                raise ValueError(f"Session is already stopped: {session_id}")
            
            # If currently paused, record the pause
            if session.is_paused and session.pause_start:
                pause_end = self._now_iso()
                pause_duration = int(
                    (self._parse_iso(pause_end) - self._parse_iso(session.pause_start)).total_seconds()
                )
                session.pauses.append({
                    "pause_start": session.pause_start,
                    "pause_end": pause_end,
                    "duration_seconds": pause_duration,
                })
                session.pause_start = None
            
            # Calculate total duration (excluding pauses)
            end_time = self._now_iso()
            session.end_time = end_time
            
            total_seconds = int(
                (self._parse_iso(end_time) - self._parse_iso(session.start_time)).total_seconds()
            )
            
            total_paused = sum(p["duration_seconds"] for p in session.pauses)
            session.total_duration_seconds = total_seconds - total_paused
            
            session.is_active = False
            session.is_paused = False
            
            return session
    
    def get_session(self, session_id: str) -> Optional[TimeSession]:
        """Get a session by ID."""
        with self.lock:
            return self.sessions.get(session_id)
    
    def get_active_sessions(self, employee_id: str) -> List[TimeSession]:
        """Get all active sessions for an employee."""
        with self.lock:
            return [
                s for s in self.sessions.values()
                if s.employee_id == employee_id and s.is_active
            ]
    
    def get_sessions_for_date(
        self,
        employee_id: str,
        date_str: str  # "2026-03-28"
    ) -> List[TimeSession]:
        """Get all sessions for an employee on a specific date."""
        with self.lock:
            result = []
            target_date = date_str[:10]  # Ensure YYYY-MM-DD format
            
            for session in self.sessions.values():
                if session.employee_id != employee_id:
                    continue
                
                # Check if session date matches
                session_date = session.start_time[:10]
                if session_date == target_date:
                    result.append(session)
            
            return sorted(result, key=lambda s: s.start_time)
    
    def get_daily_duration(
        self,
        employee_id: str,
        date_str: str
    ) -> Dict[str, Any]:
        """
        Get total duration for an employee on a specific date.
        
        Returns:
            {
                "date": "2026-03-28",
                "employee_id": "...",
                "total_seconds": 28800,
                "total_hours": 8.0,
                "session_count": 2,
                "sessions": [...]
            }
        """
        sessions = self.get_sessions_for_date(employee_id, date_str)
        
        # Only count completed sessions (not is_active)
        completed_sessions = [s for s in sessions if not s.is_active]
        total_seconds = sum(s.total_duration_seconds for s in completed_sessions)
        
        return {
            "date": date_str[:10],
            "employee_id": employee_id,
            "total_seconds": total_seconds,
            "total_hours": round(total_seconds / 3600, 2) if total_seconds > 0 else 0.0,
            "session_count": len(sessions),
            "completed_sessions": len(completed_sessions),
            "sessions": [s.to_dict() for s in sessions],
        }
    
    def get_duration_by_category(
        self,
        employee_id: str,
        date_str: str
    ) -> Dict[str, float]:
        """
        Get duration broken down by category for a specific date.
        
        Returns:
            {"development": 3.5, "testing": 2.0, "communication": 2.5}
        """
        sessions = self.get_sessions_for_date(employee_id, date_str)
        result = {}
        
        for session in sessions:
            if session.is_active:
                continue  # Skip active sessions
            
            category = session.category or "other"
            duration_hours = session.total_duration_seconds / 3600
            result[category] = result.get(category, 0) + duration_hours
        
        # Round to 2 decimals
        return {k: round(v, 2) for k, v in result.items()}
    
    def save_sessions_to_file(self, file_path: str) -> None:
        """
        Save all sessions to a JSON file.
        
        Args:
            file_path: Path to save to
        """
        with self.lock:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            sessions_data = [
                s.to_dict() for s in self.sessions.values()
            ]
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(sessions_data, f, ensure_ascii=False, indent=2)
    
    def load_sessions_from_file(self, file_path: str) -> None:
        """
        Load sessions from a JSON file.
        
        Args:
            file_path: Path to load from
        """
        if not Path(file_path).exists():
            return
        
        with open(file_path, "r", encoding="utf-8") as f:
            sessions_data = json.load(f)
        
        with self.lock:
            for data in sessions_data:
                session = TimeSession.from_dict(data)
                self.sessions[session.session_id] = session


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string (e.g., "2h 30m 45s")
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0:
        parts.append(f"{secs}s")
    
    # If no parts (0 seconds), return "0s"
    return " ".join(parts) if parts else "0s"


if __name__ == "__main__":
    # Demo usage
    tracker = TimeTracker()
    
    # Start a session
    session = tracker.start_session(
        employee_id="emp001",
        project="PROJECT1",
        task_id="task-123",
        category="development",
        priority="high",
        notes="Implementing API endpoint"
    )
    print(f"Started session: {session.session_id}")
    
    # Simulate work
    import time
    time.sleep(2)
    
    # Pause
    tracker.pause_session(session.session_id)
    print("Session paused")
    time.sleep(1)
    
    # Resume
    tracker.resume_session(session.session_id)
    print("Session resumed")
    time.sleep(2)
    
    # Stop
    stopped_session = tracker.stop_session(session.session_id)
    print(f"Session stopped. Duration: {format_duration(stopped_session.total_duration_seconds)}")
    print(f"Data: {json.dumps(stopped_session.to_dict(), ensure_ascii=False, indent=2)}")
