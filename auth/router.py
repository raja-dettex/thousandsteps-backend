from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from sqlalchemy.future import select

from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from models import User
from auth.service import get_token
from pydantic import BaseModel
router = APIRouter()
class UserLoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(request: Request, userlogin: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == userlogin.email)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user and User.verify_password(userlogin.password, user.password):
        token = get_token(user.username)
        return JSONResponse(status_code=201, content = { 'token' : token, 'username': user.username, 'role': user.role})
    else:
        return JSONResponse(status_code=401, content={"message": "Invalid credentials"})
    



