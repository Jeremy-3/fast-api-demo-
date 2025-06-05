import os
from sqlalchemy import Boolean,Column,Integer,String,create_engine,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session,relationship
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL =os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("Missing DATABASE_URL in environment")


engine = create_engine(DATABASE_URL)
session = Session(engine)

# defines the base model class
Base = declarative_base()  


class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,index=True)
    name=Column(String, index=True)
    email=Column(String, unique=True,index=True)
    is_active=Column(Boolean, default=True)
    hashed_password=Column(String,nullable=False)

    posts = relationship("Post",back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String,index=True,unique=True)
    content=Column(String,index=True)
    author_id=Column(Integer,ForeignKey("users.id"))
    
    author = relationship("User",back_populates="posts")

Base.metadata.create_all(bind=engine)