from pydantic import BaseModel,EmailStr

class UserBase(BaseModel):
    name:str = None
    email: EmailStr = None
    is_active:bool =True

    
class UserCreate(UserBase):
    password:str

class User(UserBase):
       id:int = None 
       
       class Config:
            orm_mode = True