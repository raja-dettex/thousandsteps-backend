from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from db import get_db
from models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    mobile: str
    role: str

@router.post("/")
async def add_user(request: Request, user: UserCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.username == user.username)
    result = await db.execute(stmt)
    existingUser = result.scalars().first()
    print(existingUser)
    print("here", db)
    if existingUser:
        
        return JSONResponse(status_code=201, content={
            'username': existingUser.username,
            'email': existingUser.email, 
            'password': existingUser.password,
            'mobile': existingUser.mobile,
            'role': existingUser.role
        })
    new_user = User(username=user.username, email = user.email , password=User.hash_password(user.password), mobile=user.mobile, role=user.role)    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return JSONResponse(status_code=201, content={
            'username': new_user.username,
            'email': new_user.email, 
            'password': new_user.password,
            'mobile': new_user.mobile,
            'role': new_user.role
        })

# admin token = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyYWphIiwiZXhwIjoxNzQ0MDExMzM5fQ.7lIWj52Qc2JXQDHL2bWRHEbdUJddnZC_PsaWZ0jQ2Og
# user token = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXIiLCJleHAiOjE3NDQwMTEzNzl9.oxyMBdh7lxtWH0VwTU37sDl_z2Ph1v1hoz2ZGo0xrk8