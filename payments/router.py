from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from db import get_db
from auth.service import get_current_user
from models import Payment, User
from typing import Optional

router = APIRouter()


class CreatePaymentRequest(BaseModel):
    amount: float
    transaction_id: str


@router.post('/add')
async def create_payment(
    payment_request: CreatePaymentRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    print('user id: ', type(int(user.id)))
    user_id = user.id
    payment = Payment(
        user_id=int(user_id),
        amount=payment_request.amount,
        transaction_id=payment_request.transaction_id
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return JSONResponse(status_code=201, content={"message": f"Payment created with id: {payment.id}"})


@router.get('/')
async def get_payments(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    stmt = select(Payment).where(Payment.user_id == user.id)
    result = await db.execute(stmt)
    payments = result.scalars().all()
    return JSONResponse(status_code=200, content={
        "payments": [{
            "id": payment.id,
            "amount": payment.amount,
            "transaction_id": payment.transaction_id
        } for payment in payments]
    })
