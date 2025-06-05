import redis
from fastapi import HTTPException

redis_client = redis.Redis(host="localhost",port="6379", db=0)

# redis_client.set("test","Hello Redis!")
# print(redis_client.get("test"))

def get_user_token(user_id: int):
    return redis_client.get(f"user_token:{user_id}")


def save_user_token(user_id: int, token: str):
    redis_client.setex(f"user_token:{user_id}", 3600, token)  # expires in 1 hour
    
# reset token 
# def save_reset_token(email:str,token:str):
#     redis_client.setex(f"reset_token:{token}",900,email)
    
    
# def get_reset_email(token:str):
#     email_bytes = redis_client.get(f"reset_token:{token}")
#     if not email_bytes:
#         raise HTTPException(status_code=400,detail="Invalid or expired token") 
#     email = email_bytes.decode("utf-8")    
#     return email


# save OTP when sent
def save_otp(email:str,otp:str):
    redis_client.setex(f"otp:{email}",300,otp)
    
def get_otp(email:str):
    otp =redis_client.get(f"otp:{email}")
    if not otp:
        raise HTTPException(status_code=400,detail="Invalid or Expired OTP")
    
    return otp.decode("utf-8")

# saving otp for the reset password
def save_reset_otp(email:str,otp:str):
    redis_client.setex(f"reset_otp:{email}",900,otp)
    
def get_reset_otp(email:str):
    otp = redis_client.get(f"reset_otp:{email}")
    if not otp:
        raise HTTPException(status_code=400,detail="Invalid or Expired OTP")
    
    return otp.decode("utf-8")
    
    