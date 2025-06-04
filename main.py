from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models
from database import get_db
from routes import router
from pathlib import Path
from auth import get_current_user
from typing import Optional

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
app.include_router(router)

@app.get("/")
def home(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[models.User] = Depends(get_current_user)
):
    articles = db.query(models.Article).order_by(models.Article.created_at.desc()).all()
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