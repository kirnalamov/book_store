# CodeBlog - A Modern Blog Platform for Developers

CodeBlog is a FastAPI-based blog platform designed specifically for developers to share code snippets, technical articles, and knowledge with the community. It features a clean, modern design and supports Markdown formatting with syntax highlighting.

## Features

- 🚀 Modern, responsive design using Tailwind CSS
- ✍️ Markdown support for article writing
- 🎨 Syntax highlighting for code blocks
- 📸 Image upload support for article covers
- 👥 User authentication system
- 💬 Comment system
- 🔍 Clean URLs with slug support

## Tech Stack

- FastAPI
- SQLAlchemy
- Jinja2 Templates
- Tailwind CSS
- SQLite Database
- Python-Markdown
- Highlight.js

## Setup

1. Clone the repository:
```bash
git clone https://github.com/kirnalamov/book_store.git
cd book_store
```

2. Установка poetry:
Для Windows
```bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```
Для Linux
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Установка настройки создания виртуального окружения в папке проекта:
```bash
poetry config virtualenvs.in-project true
```

4. Установка используемой версии python для виртуального окружения (у вас путь может отличаться):
   
bash
```bash
poetry env use "$USERPROFILE/AppData/Local/Programs/Python/Python312/python.exe"
```
cmd
```cmd
poetry env use "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
```
PowerShell
```PowerShell
poetry env use "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python312\python.exe"
```
5. Устновка зависимостей:
```bash
poetry install
```

6. Запуск приложения:
```bash
poetry run python main.py
# or 
poetry shell
python main.py
# poetry shell входит в виртуальное окружение, чтобы из него выйти введите команду exit
```

The application will be available at `http://localhost:8000`

## Project Structure

```
codeblog/
├── main.py           # Main FastAPI application
├── models.py         # SQLAlchemy models
├── database.py       # Database configuration
├── routes.py         # API routes
├── auth.py          # Authentication utilities
├── requirements.txt  # Python dependencies
├── static/          # Static files (CSS, JS)
├── templates/       # Jinja2 templates
└── uploads/         # User uploaded files
```

## Usage

1. Register a new account at `/register`
2. Log in at `/login`
3. Create new articles at `/write`
4. View articles at `/article/{slug}`
5. Comment on articles when logged in

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. # book_store
