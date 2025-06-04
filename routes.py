from fastapi import APIRouter, Depends, HTTPException, status, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
import models
from database import get_db
from auth import get_password_hash, verify_password, create_access_token, get_current_user, get_current_active_user
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import markdown2
from slugify import slugify

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        name="register.html",
        context={"request": request, "title": "Register"}
    )

@router.post("/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(password)
    new_user = models.User(username=username, email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        name="login.html",
        context={"request": request, "title": "Login"}
    )

@router.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=3600,
        expires=3600,
        samesite="lax",
        secure=False  # Set to True if using HTTPS
    )
    return response

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

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
    
    return RedirectResponse(url=f"/article/{article.slug}", status_code=status.HTTP_302_FOUND)

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

@router.post("/article/{article_id}/comment")
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
    return RedirectResponse(url=f"/article/{article.slug}", status_code=status.HTTP_302_FOUND)

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
    
    return RedirectResponse(url=f"/article/{article.slug}", status_code=status.HTTP_302_FOUND)

@router.get("/articles")
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

@router.get("/profile/{username}")
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
    articles = db.query(models.Article)\
        .filter(models.Article.author_id == user.id)\
        .order_by(models.Article.created_at.desc())\
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

@router.get("/profile/{username}/edit")
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

@router.post("/profile/{username}/edit")
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
    
    return RedirectResponse(url=f"/profile/{username}", status_code=status.HTTP_302_FOUND) 