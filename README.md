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
cd codeblog
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
# or 
uvicorn main:app --reload

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
Тестовый коммит
