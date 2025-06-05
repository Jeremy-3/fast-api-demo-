from fastapi import FastAPI
from routes.user import router as user_router
from routes.post import router as post_router
from routes.auth import router as auth_router
from routes.auth import Depends,get_current_user
app = FastAPI()

app.include_router(user_router)
app.include_router(post_router)
app.include_router(auth_router)

@app.get("/me")
def read_current_user(current_user = Depends(get_current_user)):
    return current_user