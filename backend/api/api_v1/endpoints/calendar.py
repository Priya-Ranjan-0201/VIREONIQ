from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from db.session import get_db
from db.models import User, ExternalCalendar, ApplicationEvent
from api import deps
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/auth-url")
async def get_auth_url(
    provider: str = "google",
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get the OAuth2 authorization URL for the specified provider.
    (Placeholder: In production, this would use google-auth-oauthlib)
    """
    if provider.lower() == "google":
        return {
            "url": "https://accounts.google.com/o/oauth2/v2/auth?...",
            "provider": "google"
        }
    raise HTTPException(status_code=400, detail="Provider not supported")

@router.post("/callback")
async def calendar_callback(
    code: str,
    provider: str = "google",
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Handle OAuth2 callback and store tokens.
    """
    # Simulate token exchange
    calendar = await db.execute(
        select(ExternalCalendar).where(and_(ExternalCalendar.user_id == current_user.id, ExternalCalendar.provider == provider))
    )
    ext_cal = calendar.scalars().first()
    
    if not ext_cal:
        ext_cal = ExternalCalendar(
            user_id=current_user.id,
            provider=provider,
            access_token="simulated_access_token",
            refresh_token="simulated_refresh_token",
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        db.add(ext_cal)
    else:
        ext_cal.access_token = "simulated_access_token_refreshed"
        ext_cal.expires_at = datetime.utcnow() + timedelta(hours=1)
        
    await db.commit()
    return {"status": "success", "message": f"{provider.capitalize()} Calendar connected"}

@router.get("/status")
async def get_calendar_status(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Check if any calendars are connected."""
    result = await db.execute(
        select(ExternalCalendar).where(ExternalCalendar.user_id == current_user.id)
    )
    calendars = result.scalars().all()
    return [{
        "provider": c.provider,
        "is_active": c.is_active,
        "expires_at": c.expires_at
    } for c in calendars]

@router.post("/sync-event/{event_id}")
async def sync_event_to_calendar(
    event_id: str,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Simulate syncing an application event to the connected calendar.
    """
    # Fetch event
    # result = await db.get(ApplicationEvent, event_id)
    # Check if user has connected calendar
    cal_res = await db.execute(
        select(ExternalCalendar).where(and_(ExternalCalendar.user_id == current_user.id, ExternalCalendar.is_active == True))
    )
    if not cal_res.scalars().first():
        raise HTTPException(status_code=400, detail="No active calendar connected")
    # In production: Use googleapiclient.discovery.build('calendar', 'v3', ...)
    return {"status": "success", "message": "Event synced to Google Calendar (Simulated)"}


from fastapi.responses import Response
from services import calendar_service
from db.models import PreparationCalendar

@router.post("/generate-ics")
async def generate_student_prep_ics(
    payload: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Response:
    """
    Generate and download the iCalendar (.ics) format of the student preparation plan calendar.
    Supports dynamic tasks provided in request payload or saved database plans.
    """
    tasks = None
    if payload and isinstance(payload, dict) and payload.get("tasks"):
        tasks = payload["tasks"]
    
    if not tasks:
        stmt = select(PreparationCalendar).where(PreparationCalendar.user_id == current_user.id).order_by(PreparationCalendar.created_at.desc())
        plan = (await db.execute(stmt)).scalars().first()
        if plan and plan.daily_tasks:
            tasks = plan.daily_tasks

    if not tasks:
        # Generate full default 30-day curriculum
        from datetime import datetime, timezone, timedelta
        base_date = datetime.now(timezone.utc)
        TOPICS = [
            ("Arrays & Two Pointers", ["Solve 3 LeetCode Easy/Medium", "Review Two-Pointer & Sliding Window"]),
            ("Strings & Hash Maps", ["Anagram & Palindrome patterns", "Prefix Sum techniques"]),
            ("Linked Lists", ["Cycle Detection (Floyd's)", "Reverse Linked List in-place"]),
            ("Stacks & Queues", ["Monotonic Stack pattern", "Daily Temperatures problem"]),
            ("Binary Search", ["Search in Rotated Sorted Array", "Binary search on answer domain"]),
            ("Recursion & Backtracking", ["Subsets & Permutations", "N-Queens constraint satisfaction"]),
            ("Binary Trees", ["Tree traversals (Inorder/Preorder/Postorder)", "Lowest Common Ancestor"]),
            ("Binary Search Trees", ["Validate BST", "Kth Smallest Element in BST"]),
            ("Heaps & Priority Queues", ["Top K Frequent Elements", "Merge K Sorted Lists"]),
            ("Graph Fundamentals", ["BFS & DFS on Adjacency Lists", "Connected Components"]),
            ("Shortest Paths", ["Dijkstra's Algorithm with Min-Heap", "Bellman-Ford & Negative Cycles"]),
            ("Dynamic Programming I", ["1D DP (Climbing Stairs, House Robber)", "Coin Change memoization"]),
            ("Dynamic Programming II", ["Longest Common Subsequence", "0/1 Knapsack problem"]),
            ("System Design Basics", ["Horizontal vs Vertical Scaling", "Load Balancing (Nginx, HAProxy)"]),
            ("Distributed Caching", ["Redis Cache-Aside Pattern", "Cache Stampede & Eviction Policies"]),
            ("Database Internals", ["B+ Tree Indexes vs Hash Indexes", "ACID & Isolation Levels"]),
            ("Operating Systems", ["Processes vs Threads & Concurrency", "Deadlocks & Coffman Conditions"]),
            ("Computer Networks", ["TCP Handshake & TIME_WAIT (2MSL)", "HTTP/2 vs HTTP/3 QUIC"]),
            ("Object-Oriented Design", ["SOLID Principles in Practice", "Design Patterns (Factory, Singleton)"]),
            ("Behavioral & Leadership", ["Amazon Leadership Principles (STAR)", "Conflict Resolution Stories"])
        ]
        tasks = [
            {
                "day": i + 1,
                "topic": TOPICS[i % len(TOPICS)][0],
                "tasks": TOPICS[i % len(TOPICS)][1],
                "date": (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
            }
            for i in range(30)
        ]
    
    ics_string = calendar_service.generate_ics_calendar(current_user.id, tasks)
    
    return Response(
        content=ics_string,
        media_type="text/calendar",
        headers={"Content-Disposition": "attachment; filename=vireoniq_prep_plan.ics"}
    )

