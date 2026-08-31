"""
Preparation Calendar export service.
Generates RFC-compliant iCalendar (.ics) files from study plans.
"""
from typing import List, Dict, Any
from datetime import datetime, timezone
import uuid


def generate_ics_calendar(
    user_id: uuid.UUID,
    daily_tasks: List[Dict[str, Any]]
) -> str:
    """
    Generate an iCalendar (.ics) file content string.
    Each day with tasks is represented as a VEVENT.
    """
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//VIREONIQ//Placement Prep Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]
    
    for task in daily_tasks:
        day_num = task.get("day", 1)
        topic = task.get("topic", "General Prep")
        tasks = task.get("tasks", [])
        date_str = task.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        
        # Parse task date: expected YYYY-MM-DD
        formatted_date = date_str.replace("-", "")
        
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uuid.uuid4()}@vireoniq.com",
            f"DTSTAMP:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART;VALUE=DATE:{formatted_date}",
            f"DTEND;VALUE=DATE:{formatted_date}",
            f"SUMMARY:VIREONIQ Day {day_num} - {topic}",
            f"DESCRIPTION:Tasks:\\n" + "\\n".join([f"- {t}" for t in tasks]),
            "END:VEVENT"
        ])
        
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)
