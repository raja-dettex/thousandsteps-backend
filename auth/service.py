import jwt

from typing import Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, Security, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.future import select
from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from models import User
ALGORITHM = "HS256"
JWT_SECRET='your_jwt_secret_key'
EXPIRE_MINUTES = 30
oauth2scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

def get_token(username: str, expires_delta: Optional[timedelta]=None):
    expires = datetime.utcnow() + (expires_delta or  timedelta(minutes=EXPIRE_MINUTES))
    data = { 'sub': username, 'exp': expires}
    return jwt.encode(data, JWT_SECRET, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='signature has expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="invalid token")
    

async def get_current_user(token : str = Security(oauth2scheme), db: AsyncSession = Depends(get_db)) -> User:
    payload = verify_token(token)
    username = payload['sub']
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalars().first()
    print(user)
    return user