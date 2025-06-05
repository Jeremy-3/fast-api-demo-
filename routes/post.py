from fastapi import APIRouter,HTTPException
from typing import List
from models import Post as post_model
from models import session
from schema.post_schema import PostBase,PostCreate,Post
from routes.auth import get_current_user,Depends

router = APIRouter(prefix="/posts",tags=["posts"],dependencies=[Depends(get_current_user)])

@router.post("",response_model=Post)
def create_post(post:PostCreate):
    try:
        db_post = post_model(**post.dict())
        session.add(db_post)
        session.commit()
        session.refresh(db_post)
        return db_post
    except Exception as e:
        raise HTTPException(status_code=404,detail=str(e))
    
@router.get("",response_model=List[Post])
def get_posts(skip:int=0,limit:int=100):
    post=session.query(post_model).offset(skip).limit(limit).all()
    return post

@router.get("/{post_id}",response_model=Post)
def get_post(post_id:int):
    post=session.query(post_model).filter(post_model.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404,detail="Post not found")
    return post

@router.put("/{post_id}",response_model=Post)
def update_post(post_id:int,update_post:PostBase):
    db_post = session.query(post_model).filter(post_model.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404,detail="Post not found")
    
    for key,value in update_post.dict().items():
        setattr(db_post,key,value)
        
    session.commit()
    session.refresh(db_post)
    return db_post    