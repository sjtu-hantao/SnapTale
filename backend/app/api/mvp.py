import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field
from sqlmodel import Session

from database import get_db

from .mvp_service import apply_feedback, bootstrap_user, generate_collection_content, get_growth_view

router = APIRouter()


class BootstrapRequest(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = "Creator"


class FeedbackRequest(BaseModel):
    user_id: str
    signal_type: str
    rating: Optional[int] = Field(default=None, ge=-2, le=2)
    tags: List[str] = Field(default_factory=list)
    rewrite_text: str = ""


@router.post("/bootstrap")
def bootstrap(payload: BootstrapRequest, db: Session = Depends(get_db)):
    try:
        user, profile = bootstrap_user(db, payload.user_id, payload.username)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "user": {
            "user_id": str(user.user_id),
            "username": user.username,
        },
        "profile": {
            "preference_id": str(profile.preference_id),
            "summary": profile.summary,
        },
    }


@router.post("/generate")
def generate_storyboard(
    request: Request,
    user_id: str = Form(...),
    title: str = Form("Untitled Moment"),
    context: str = Form(""),
    photos: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    try:
        parsed_user_id = uuid.UUID(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid user_id format.") from exc

    user, profile = bootstrap_user(db, str(parsed_user_id), None)
    backend_base_url = str(request.base_url).rstrip("/")
    try:
        return generate_collection_content(
            db=db,
            user=user,
            profile=profile,
            title=title,
            context=context,
            files=photos,
            backend_base_url=backend_base_url,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/posts/{post_id}/feedback")
def submit_feedback(post_id: str, payload: FeedbackRequest, db: Session = Depends(get_db)):
    if payload.signal_type not in {"like", "dislike", "select", "rewrite"}:
        raise HTTPException(status_code=400, detail="Unsupported signal_type.")

    try:
        parsed_post_id = uuid.UUID(post_id)
        parsed_user_id = uuid.UUID(payload.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid identifier format.") from exc

    try:
        return apply_feedback(
            db=db,
            user_id=parsed_user_id,
            post_id=parsed_post_id,
            signal_type=payload.signal_type,
            rating=payload.rating,
            tags=payload.tags,
            rewrite_text=payload.rewrite_text,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/users/{user_id}/growth")
def growth(user_id: str, db: Session = Depends(get_db)):
    try:
        parsed_user_id = uuid.UUID(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid user_id format.") from exc

    try:
        return get_growth_view(db, parsed_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
