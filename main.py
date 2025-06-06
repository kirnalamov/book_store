from pathlib import Path
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user
from typing import Optional
from routers.auth_router import router as auth_router
from routers.articles_router import router as articles_router
from routers.books import router as books_router
from routers.comments_router import router as comments_router
from routers.profiles_router import router as profiles_router

# Create upload directory if it doesn't exist
Path("uploads").mkdir(exist_ok=True)

app = FastAPI(title="CodeBlog")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Templates
templates = Jinja2Templates(directory="templates")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_router)
app.include_router(articles_router)
app.include_router(books_router)
app.include_router(comments_router)
app.include_router(profiles_router)


@app.get("/")
def home(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[models.User] = Depends(get_current_user)
):
    articles = db.query(models.Article).order_by(
        models.Article.created_at.desc()).all()
    return templates.TemplateResponse(
        name="index.html",
        context={
            "request": request,
            "title": "CodeBlog - Share Your Knowledge",
            "articles": articles,
            "user": user
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
