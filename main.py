from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from users.router import router
from auth.router import router as auth_router
from orders.router import router as orders_router
from payments.router import router as payments_router
from trips.router import router as trips_router
from db import init_db 
import asyncio

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
app.include_router(router, prefix='/v1/users')
app.include_router(trips_router, prefix='/v1/trips')
app.include_router(auth_router, prefix ='/v1/auth')
app.include_router(orders_router, prefix='/v1/orders')
app.include_router(payments_router, prefix ='/v1/payments')
@app.on_event('startup')
async def init(): 
    await init_db()


uvicorn.run(app, host='0.0.0.0', port=8000.)
