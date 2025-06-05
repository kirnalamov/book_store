from fastapi import APIRouter, Depends, status, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import models
from database import get_db
from auth import get_current_active_user

router = APIRouter(
    prefix="/comments",
    tags=["comments"]
)


@router.post("/article/{article_id}")
async def add_comment(
    article_id: int,
    content: str = Form(...),
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    comment = models.Comment(
        content=content,
        article_id=article_id,
        author_id=user.id
    )
    db.add(comment)
    db.commit()
    
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    return RedirectResponse(url=f"/articles/article/{article.slug}", status_code=status.HTTP_302_FOUND)
