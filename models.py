from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from slugify import slugify

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    bio = Column(Text, nullable=True)
    avatar_path = Column(String(500), nullable=True)
    website = Column(String(200), nullable=True)
    github_username = Column(String(100), nullable=True)
    twitter_username = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    articles = relationship("Article", back_populates="author")
    comments = relationship("Comment", back_populates="author")

    @property
    def total_views(self):
        return sum(article.views for article in self.articles)

    @property
    def total_comments(self):
        return sum(len(article.comments) for article in self.articles)

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    slug = Column(String(250), unique=True, index=True)
    content = Column(Text)
    code_snippet = Column(Text, nullable=True)
    image_path = Column(String(500), nullable=True)
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="articles")
    comments = relationship("Comment", back_populates="article")
    
    def generate_slug(self):
        return slugify(self.title)

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    author_id = Column(Integer, ForeignKey("users.id"))
    article_id = Column(Integer, ForeignKey("articles.id"))
    author = relationship("User", back_populates="comments")
    article = relationship("Article", back_populates="comments")

# Database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create tables
Base.metadata.create_all(bind=engine) 