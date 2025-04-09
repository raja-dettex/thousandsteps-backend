from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from db import get_db
from auth.service import get_current_user
from models import Order, User, Trip, Payment

router = APIRouter()


class CreateOrderRequest(BaseModel):
    trip_id: int
    payment_id: int


@router.post('/add')
async def create_order(
    order_request: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if user.role != 'user':
        return JSONResponse(status_code = 401, content = { 'message': 'admin can not create order'})
    # Check if the trip exists
    trip = await db.get(Trip, order_request.trip_id)
    if not trip:
        return JSONResponse(status_code=404, content={"message": "Trip not found"})

    # Check if the payment exists and belongs to the user
    payment = await db.get(Payment, order_request.payment_id)
    if not payment or payment.user_id != user.id:
        return JSONResponse(status_code=403, content={"message": "Invalid or unauthorized payment"})

    order = Order(
        user_id=user.id,
        trip_id=order_request.trip_id,
        payment_id=order_request.payment_id
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return JSONResponse(status_code=201, content={"message": f"Order created with id: {order.id}"})


@router.get('/')
async def get_orders(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    stmt = select(Order).where(Order.user_id == user.id)
    result = await db.execute(stmt)
    orders = result.scalars().all()
    return JSONResponse(status_code=200, content={
        "orders": [{
            "order_id": order.id,
            "trip_id": order.trip_id,
            "payment_id": order.payment_id
        } for order in orders]
    })
