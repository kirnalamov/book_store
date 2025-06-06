from fastapi import APIRouter, Depends, HTTPException, status, Request, File, UploadFile, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
import models
from database import get_db
from auth import get_current_user, get_current_active_user
import shutil
from datetime import datetime
import markdown2
from slugify import slugify

router = APIRouter(
    prefix="/articles",
    tags=["articles"]
)
templates = Jinja2Templates(directory="templates")


@router.get("/write")
def write_article_page(
        request: Request,
        user: models.User = Depends(get_current_active_user)
):
    return templates.TemplateResponse(
        name="write.html",
        context={"request": request, "title": "Write Article", "user": user}
    )


@router.post("/write")
async def create_article(
        title: str = Form(...),
        content: str = Form(...),
        image: Optional[UploadFile] = File(None),
        user: models.User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    article = models.Article(
        title=title,
        content=content,
        author_id=user.id,
        slug=slugify(title)
    )

    if image:
        file_location = f"uploads/{datetime.now().strftime('%Y%m%d%H%M%S')}_{image.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
        article.image_path = file_location.replace("uploads/", "")

    db.add(article)
    db.commit()

    return RedirectResponse(url=f"/articles/article/{article.slug}", status_code=status.HTTP_302_FOUND)


@router.get("/article/{slug}")
def read_article(
        request: Request,
        slug: str,
        db: Session = Depends(get_db),
        user: Optional[models.User] = Depends(get_current_user)
):
    article = db.query(models.Article).filter(models.Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Increment view count
    article.views += 1
    db.commit()

    html_content = markdown2.markdown(article.content, extras=["fenced-code-blocks"])
    return templates.TemplateResponse(
        name="article.html",
        context={
            "request": request,
            "title": article.title,
            "article": article,
            "content": html_content,
            "user": user
        }
    )


@router.get("/article/{slug}/edit")
def edit_article_page(
        request: Request,
        slug: str,
        db: Session = Depends(get_db),
        user: models.User = Depends(get_current_active_user)
):
    article = db.query(models.Article).filter(models.Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if article.author_id != user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own articles")

    return templates.TemplateResponse(
        name="edit.html",
        context={
            "request": request,
            "title": f"Edit - {article.title}",
            "article": article,
            "user": user
        }
    )


@router.post("/article/{slug}/edit")
async def edit_article(
        slug: str,
        title: str = Form(...),
        content: str = Form(...),
        image: Optional[UploadFile] = File(None),
        user: models.User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    article = db.query(models.Article).filter(models.Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if article.author_id != user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own articles")

    article.title = title
    article.content = content
    article.slug = slugify(title)
    article.updated_at = datetime.utcnow()

    if image:
        file_location = f"uploads/{datetime.now().strftime('%Y%m%d%H%M%S')}_{image.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
        article.image_path = file_location.replace("uploads/", "")

    db.commit()

    return RedirectResponse(url=f"/articles/article/{article.slug}", status_code=status.HTTP_302_FOUND)


@router.get("")
def list_articles(
        request: Request,
        db: Session = Depends(get_db),
        user: Optional[models.User] = Depends(get_current_user)
):
    articles = db.query(models.Article).order_by(models.Article.created_at.desc()).all()
    return templates.TemplateResponse(
        name="articles.html",
        context={
            "request": request,
            "title": "All Articles",
            "articles": articles,
            "user": user
        }
    )
