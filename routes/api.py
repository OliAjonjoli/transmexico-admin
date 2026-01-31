from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional
import sys
import os

from settings import settings
from db import get_db

# Import bot database models
bot_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../bot'))
sys.path.insert(0, bot_path)
from database import Member, Presentation

router = APIRouter(prefix="/api", tags=["presentations"])


@router.get("/presentations")
async def list_presentations(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get list of presentations with optional filtering."""
    query = select(Presentation)
    
    if status:
        query = query.where(Presentation.status == status)
    
    query = query.offset(offset).limit(limit)
    presentations = db.execute(query).scalars().all()
    
    # Get total count
    total = db.execute(select(Presentation)).scalars().all()
    
    return {
        "total": len(total),
        "limit": limit,
        "offset": offset,
        "items": [
            {
                "id": p.id,
                "member_id": p.member_id,
                "discord_message_id": p.discord_message_id,
                "content": p.content[:200] + "..." if len(p.content) > 200 else p.content,
                "status": p.status,
                "auto_suggestion": p.auto_suggestion,
                "message_timestamp": p.message_timestamp.isoformat() if p.message_timestamp else None,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat(),
            }
            for p in presentations
        ]
    }


@router.get("/presentations/{presentation_id}")
async def get_presentation(presentation_id: int, db: Session = Depends(get_db)):
    """Get a single presentation with member info."""
    presentation = db.execute(
        select(Presentation).where(Presentation.id == presentation_id)
    ).scalar_one_or_none()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    member = db.execute(
        select(Member).where(Member.id == presentation.member_id)
    ).scalar_one_or_none()
    
    return {
        "id": presentation.id,
        "member": {
            "id": member.id,
            "discord_id": member.discord_id,
            "username": member.username,
        } if member else None,
        "content": presentation.content,
        "status": presentation.status,
        "auto_suggestion": presentation.auto_suggestion,
        "suggestion_reason": presentation.suggestion_reason,
        "message_timestamp": presentation.message_timestamp.isoformat() if presentation.message_timestamp else None,
        "created_at": presentation.created_at.isoformat(),
        "updated_at": presentation.updated_at.isoformat(),
    }


@router.post("/presentations/{presentation_id}/approve")
async def approve_presentation(
    presentation_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    """Approve a presentation."""
    from auth import verify_token
    
    token_data = verify_token(token)
    if not token_data or not token_data.is_staff:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    presentation = db.execute(
        select(Presentation).where(Presentation.id == presentation_id)
    ).scalar_one_or_none()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    presentation.status = "approved"
    presentation.reviewed_by = token_data.discord_id
    from datetime import datetime
    presentation.reviewed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(presentation)
    
    return {
        "id": presentation.id,
        "status": presentation.status,
        "reviewed_by": presentation.reviewed_by,
        "reviewed_at": presentation.reviewed_at.isoformat(),
    }


@router.post("/presentations/{presentation_id}/reject")
async def reject_presentation(
    presentation_id: int,
    reason: str = Query(None),
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    """Reject a presentation."""
    from auth import verify_token
    
    token_data = verify_token(token)
    if not token_data or not token_data.is_staff:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    presentation = db.execute(
        select(Presentation).where(Presentation.id == presentation_id)
    ).scalar_one_or_none()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    presentation.status = "rejected"
    presentation.reviewed_by = token_data.discord_id
    if reason:
        presentation.suggestion_reason = reason
    
    from datetime import datetime
    presentation.reviewed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(presentation)
    
    return {
        "id": presentation.id,
        "status": presentation.status,
        "reason": presentation.suggestion_reason,
        "reviewed_by": presentation.reviewed_by,
        "reviewed_at": presentation.reviewed_at.isoformat(),
    }


@router.get("/members")
async def list_members(
    has_presentation: Optional[bool] = Query(None),
    verified: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get list of members."""
    query = select(Member)
    
    if has_presentation is not None:
        query = query.where(Member.has_presentation == has_presentation)
    
    if verified is not None:
        query = query.where(Member.verified_role_assigned == verified)
    
    query = query.offset(offset).limit(limit)
    members = db.execute(query).scalars().all()
    
    # Get total count
    total = db.execute(select(Member)).scalars().all()
    
    return {
        "total": len(total),
        "limit": limit,
        "offset": offset,
        "items": [
            {
                "id": m.id,
                "discord_id": m.discord_id,
                "username": m.username,
                "has_presentation": m.has_presentation,
                "verified_role_assigned": m.verified_role_assigned,
                "joined_at": m.joined_at.isoformat(),
            }
            for m in members
        ]
    }


@router.get("/members/{member_id}")
async def get_member(member_id: int, db: Session = Depends(get_db)):
    """Get member with their presentations."""
    member = db.execute(
        select(Member).where(Member.id == member_id)
    ).scalar_one_or_none()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    presentations = db.execute(
        select(Presentation).where(Presentation.member_id == member_id)
    ).scalars().all()
    
    return {
        "id": member.id,
        "discord_id": member.discord_id,
        "username": member.username,
        "has_presentation": member.has_presentation,
        "verified_role_assigned": member.verified_role_assigned,
        "joined_at": member.joined_at.isoformat(),
        "presentations": [
            {
                "id": p.id,
                "content": p.content[:200] + "..." if len(p.content) > 200 else p.content,
                "status": p.status,
                "created_at": p.created_at.isoformat(),
            }
            for p in presentations
        ],
    }


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics."""
    total_members = db.execute(select(Member)).scalars().all()
    total_presentations = db.execute(select(Presentation)).scalars().all()
    
    approved = [p for p in total_presentations if p.status == "approved"]
    pending = [p for p in total_presentations if p.status == "pending"]
    auto_suggested = [p for p in total_presentations if p.status == "auto_suggested"]
    
    return {
        "total_members": len(total_members),
        "members_with_presentations": sum(1 for m in total_members if m.has_presentation),
        "members_verified": sum(1 for m in total_members if m.verified_role_assigned),
        "total_presentations": len(total_presentations),
        "approved_presentations": len(approved),
        "pending_presentations": len(pending),
        "auto_suggested_presentations": len(auto_suggested),
    }
