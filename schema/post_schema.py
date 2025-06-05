from pydantic import BaseModel


class PostBase(BaseModel):
    title:str = None
    content:str = None
    
class PostCreate(PostBase):
    author_id:int

class Post(PostBase):
    id:int = None
    # author_id:int    
    
    class Config:
        orm_mode = True