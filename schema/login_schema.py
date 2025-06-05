from pydantic import BaseModel,EmailStr

class LoginRequest(BaseModel):
    email:EmailStr
    password:str
    
class ForgotPassword(BaseModel):
    email:EmailStr
    
class ResetPassword(BaseModel):
    email:EmailStr
    otp: str
    new_password: str
    
    
class OTPVerifyRequest(BaseModel):
    email:EmailStr 
    otp:str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str       
    
    
    
    