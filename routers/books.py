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
#import markdown2
import base64
import os
from slugify import slugify
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF

router = APIRouter(
    prefix="/books",
    tags=["books"]
)
templates = Jinja2Templates(directory="templates")


@router.get("/add")
def add_book_page(
        request: Request,
        user: models.User = Depends(get_current_active_user)
):
    return templates.TemplateResponse(
        name="book_adding.html",
        context={"request": request, "title": "Write Book", "user": user}
    )


@router.post("/add")
async def create_book(
        title: str = Form(...),
        description: str = Form(...),
        cover: Optional[UploadFile] = File(None),
        book: Optional[UploadFile] = File(),
        user: models.User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    book_to_add = models.Book(
        title=title,
        description=description,
        author_id=user.id,
        slug=slugify(title)
    )

    # сохранение книги
    book_location = f"uploads/{datetime.now().strftime('%Y%m%d%H%M%S')}_{secure_filename(book.filename)}"
    with open(book_location, "wb+") as book_object:
        shutil.copyfileobj(book.file, book_object)
    book_to_add.pdf_path = book_location.replace("uploads/", "")

    # сохранение превью книги
    pdf_document = fitz.open(book_location)
    if pdf_document.page_count < 1:
        pdf_document.close()
        raise HTTPException(status_code=400, detail="PDF is empty")

    page = pdf_document.load_page(0)

    # Рендерим страницу в изображение
    pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))  # Масштаб 50% (0.5x)
    cover_location = book_location[:-4] + "_cover.png"
    pix.save(cover_location, "PNG")

    pdf_document.close()

    book_to_add.cover_path = cover_location.replace("uploads/", "")

    db.add(book_to_add)
    db.commit()

    return RedirectResponse(url="/books", status_code=status.HTTP_302_FOUND)

@router.get("/pdf_meta/{book_id}")
def get_pdf_meta(book_id: str, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.slug == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    file_path = os.path.join("uploads", book.pdf_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл книги не найден")

    with fitz.open(file_path) as doc:
        return {"total_pages": doc.page_count}


@router.get("/read/{book_id}")
def read_book_page(
    request: Request,
    book_id: str,
    db: Session = Depends(get_db),
    user: Optional[models.User] = Depends(get_current_user)
):
    
    book = db.query(models.Book).filter(models.Book.slug == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    return templates.TemplateResponse(
        "read_book.html",
        {
            "request": request,
            "book": book,
            "title": f"Чтение - {book.title}",
            "user": user
        }
    )


@router.get("/pdf_page/{book_id}/{page_number}")
def get_pdf_page(
    book_id: str,
    page_number: int,
    db: Session = Depends(get_db)
):
    book = db.query(models.Book).filter(models.Book.slug == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    file_path = os.path.join("uploads", book.pdf_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл книги не найден")

    with fitz.open(file_path) as doc:
        if page_number < 1 or page_number > doc.page_count:
            raise HTTPException(status_code=400, detail="Неверный номер страницы")

        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=page_number - 1, to_page=page_number - 1)
        pdf_bytes = new_doc.write()

        encoded = base64.b64encode(pdf_bytes).decode('utf-8')
        return {"data": encoded}


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
    books = db.query(models.Book).order_by(models.Book.created_at.desc()).all()
    return templates.TemplateResponse(
        name="books.html",
        context={
            "request": request,
            "title": "All Books",
            "books": books,
            "user": user
        }
    )
