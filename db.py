from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
import ssl
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


import os
database_url = os.getenv('DATABASE_URI')
print(database_url)
engine = create_async_engine(database_url, echo=True, connect_args = { "ssl": ssl_context})

sessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, autoflush=True, expire_on_commit=False)
Base = declarative_base()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with  sessionLocal() as session:
        print(session)
        yield session
