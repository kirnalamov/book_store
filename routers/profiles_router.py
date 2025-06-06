from fastapi import (APIRouter, Depends, HTTPException, status, Request, File,
                     UploadFile, Form)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
import models
from database import get_db
from auth import get_current_user, get_current_active_user
from datetime import datetime
import shutil

router = APIRouter(
    prefix="/profiles",
    tags=["profiles"]
)
templates = Jinja2Templates(directory="templates")


@router.get("/{username}")
def view_profile(
        request: Request,
        username: str,
        db: Session = Depends(get_db),
        current_user: Optional[models.User] = Depends(get_current_user)
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get user's articles with their stats
    articles = db.query(models.Article) \
        .filter(models.Article.author_id == user.id) \
        .order_by(models.Article.created_at.desc()) \
        .all()

    # Calculate contribution stats (similar to GitHub's contribution graph)
    today = datetime.utcnow().date()
    contribution_data = {}
    for article in articles:
        date_key = article.created_at.date().isoformat()
        if date_key in contribution_data:
            contribution_data[date_key]["count"] += 1
            contribution_data[date_key]["views"] += article.views
        else:
            contribution_data[date_key] = {
                "count": 1,
                "views": article.views
            }

    return templates.TemplateResponse(
        name="profile.html",
        context={
            "request": request,
            "title": f"{username}'s Profile",
            "profile_user": user,
            "current_user": current_user,
            "articles": articles,
            "contribution_data": contribution_data
        }
    )


@router.get("/{username}/edit")
def edit_profile_page(
        request: Request,
        username: str,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user)
):
    if current_user.username != username:
        raise HTTPException(status_code=403, detail="You can only edit your own profile")

    return templates.TemplateResponse(
        name="edit_profile.html",
        context={
            "request": request,
            "title": "Edit Profile",
            "user": current_user
        }
    )


@router.post("/{username}/edit")
async def edit_profile(
        username: str,
        bio: str = Form(None),
        website: str = Form(None),
        github_username: str = Form(None),
        twitter_username: str = Form(None),
        avatar: Optional[UploadFile] = File(None),
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user)
):
    if current_user.username != username:
        raise HTTPException(status_code=403, detail="You can only edit your own profile")

    current_user.bio = bio
    current_user.website = website
    current_user.github_username = github_username
    current_user.twitter_username = twitter_username

    if avatar:
        file_location = f"uploads/{datetime.now().strftime('%Y%m%d%H%M%S')}_{avatar.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(avatar.file, file_object)
        current_user.avatar_path = file_location.replace("uploads/", "")

    db.commit()

    return RedirectResponse(url=f"/profiles/{username}", status_code=status.HTTP_302_FOUND)
