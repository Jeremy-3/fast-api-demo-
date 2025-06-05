from fastapi import APIRouter
from fastapi import HTTPException
from typing import List
from models import session
from models import User as user_model
from schema.user_schema import UserCreate,UserBase,User
from routes.auth import hash_password

router = APIRouter(prefix="/users",tags=["users"])




@router.post("", response_model=User, status_code=201)
def create_user(user: UserCreate):
    # Use email from the model instead of separate argument
    existing_user = session.query(user_model).filter(user_model.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already in use")

    # Hash the password
    hashed_pw = hash_password(user.password)

    # Create new user object with hashed password
    db_user = user_model(
        name=user.name,
        email=user.email,
        hashed_password=hashed_pw
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
    
@router.get("",response_model=List[User])
def read_users(skip: int=0,limit:int=100):
    users = session.query(user_model).offset(skip).limit(limit).all()
    # print(users)
    return users
      
@router.get("/{user_id}",response_model=User)
def read_user(user_id:int):
          user = session.query(user_model).filter(user_model.id == user_id).first()
          if user is None:
              raise HTTPException(status_code=404,detail="User not found")
          return user   
      
@router.put("/{user_id}",response_model=User)
def update_user(user_id:int,user_update:UserBase):
    db_user=session.query(user_model).filter(user_model.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404,detail="User not found")
    
    for key,value in user_update.dict().items():
        setattr(db_user,key,value)
        
    session.commit()
    session.refresh(db_user)
    return db_user    