from fastapi import APIRouter,HTTPException,Depends
from datetime import datetime,timedelta
from models import session
from models import User as user_model
from schema.login_schema import LoginRequest,ForgotPassword,ResetPassword,OTPVerifyRequest,TokenResponse
import bcrypt
import jwt
import os
from dotenv import load_dotenv
from cache import save_otp ,get_otp,save_reset_otp, get_reset_otp
import random
from fastapi.security import OAuth2PasswordBearer
from helpers.mail import fm 
from fastapi_mail import MessageSchema
import asyncio
# from starlette.responses import JSONResponse




load_dotenv()

router = APIRouter(prefix="/login",tags=["logins"])

SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# password hashing before storing and verify's password with the hash one
def hash_password(password:str) -> str:
    salt = bcrypt.gensalt()
    hashed =bcrypt.hashpw(password.encode('utf-8'),salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )




# creating access token after user is logged in
def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)


def decode_access_token(token:str):
    try:
        payload = jwt.decode(token, SECRET_KEY,algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401,detail="Invalid token,Try to login again")
    
# reset token for resetting the password    
# def create_reset_token(email:str):
#     expire = datetime.now() + timedelta(minutes=15)
#     return jwt.encode({"sub":email,"exp":"expire"},SECRET_KEY,algorithm=ALGORITHM)


# functions to generate otp's
def generate_otp():
    return f"{random.randint(100000,999999)}"

# def send_otp_email(email:str,otp:str):
#     print(f"[EMAIL SENT] OTP for {email} is: {otp}")

async def send_otp_email(email:str,otp:str):
    message=MessageSchema(
        subject="Your 2-Step verification OTP",
        recipients =[email],
        body=f"Your OTP is: <strong>{otp}</strong>",
        subtype="html"
    ) 
    
    await fm.send_message(message)   
    # return  JSONResponse(status_code=200, content={"message": "email has been sent"})
    
# message for email for forgot password
async def reset_otp_email(email:str,otp:str):
        message=MessageSchema(
        subject="Your Reset OTP",
        recipients =[email],
        body=f"Your OTP is: <strong>{otp}</strong>",
        subtype="html"
    ) 
    
        await fm.send_message(message)

# message to verify your login 
async def verify_login_email(email:str,otp:str):
        message=MessageSchema(
        subject="Your Have successfully logged in",
        recipients =[email],
        body=f"Thank you for logging in we value your <strong>Privacy</strong>",
        subtype="html"
    ) 
    
        await fm.send_message(message)    




# Get current user with the tokens
oath2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_oath_schema():
    return (oath2_scheme)

def get_current_user(token:str =Depends(oath2_scheme)):
    email = decode_access_token(token)
    
    user = session.query(user_model).filter(user_model.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


# Routes for Login 
@router.post("")
async def login(credentials:LoginRequest):
    user = session.query(user_model).filter(user_model.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password,user.hashed_password):
        raise HTTPException(status_code=400,detail="Invalid Credentials")
    
    # access_token = create_access_token(data={"sub":user.email})
    otp =generate_otp()
    save_otp(user.email, otp)
    # send_otp_email(user.email, otp)
    asyncio.create_task(send_otp_email(user.email, otp))
    
    return {"message":f"OTP for: {user.email} is: {otp}"}    
    
    
@router.post("/forgot-password")    
async def forgot_password(request:ForgotPassword):
    user= session.query(user_model).filter(user_model.email == request.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    otp = generate_otp()
    save_reset_otp(user.email,otp)
    asyncio.create_task(reset_otp_email(user.email, otp))
    # print(f"Reset OTP for {user.email} is: {otp}")
    
    return {"message":f"Reset OTP for:{user.email} is: {otp}"}
    
    
@router.post("/reset-password")
def reset_password(newEntry:ResetPassword):   
    stored_otp =get_reset_otp(newEntry.email)
    reset_otp = newEntry.otp
    
    user = session.query(user_model).filter(user_model.email == newEntry.email).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    
    if stored_otp != reset_otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    
    user.hashed_password = hash_password(newEntry.new_password)
    session.commit()
    session.refresh(user)
    # redis_client.delete(f"reset_token:{token}")
    
    return {"Message":"Password reset successfully"}

@router.post("/verify-otp",response_model=TokenResponse)
async def verify_otp(entry:OTPVerifyRequest):
    user_otp = entry.otp
    stored_otp =get_otp(entry.email)
    
    if stored_otp != user_otp:
        raise HTTPException(status_code=400,detail="Invalid Otp")
    
    access_token = create_access_token(data={"sub":entry.email})
    
    asyncio.create_task(verify_login_email(entry.email, entry.otp))

      
    return{
        "access_token":access_token,
        "token_type":"bearer"
    }
    
    