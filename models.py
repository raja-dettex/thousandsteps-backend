# common imports
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from db import Base
from passlib.context import CryptContext
from datetime import datetime
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------- User --------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    mobile = Column(String)
    role = Column(String)

    orders = relationship("Order", back_populates="user")
    payments = relationship("Payment", back_populates="user")

    def __init__(self, username, email, password, mobile, role):
        self.username = username
        self.email = email
        self.password = password
        self.mobile = mobile
        self.role = role

    def hash_password(password: str):
        return pwd_context.hash(password)

    def verify_password(plain_password: str, hashed_password: str):
        return pwd_context.verify(plain_password, hashed_password)


# -------------------- Trip --------------------

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    distance_km = Column(Float, nullable=False)
    start_time = Column(DateTime(timezone=True), default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="ongoing")  
    original_price = Column(Float, nullable=False)
    discounted_price = Column(Float, nullable=False)
    slots_left = Column(Integer, nullable=False)
    image_url = Column(String,  nullable=True)
    offerings = Column(ARRAY(String), nullable=False)

    orders = relationship("Order", back_populates="trip")

    def __init__(self, title, origin, destination, distance_km, start_time, end_time, status, original_price, discounted_price, slots_left, image_url, offerings):
        self.origin = origin
        self.title = title
        self.destination = destination
        self.distance_km = distance_km
        self.start_time = start_time
        self.end_time = end_time 
        self.original_price = original_price
        self.discounted_price = discounted_price
        self.slots_left = slots_left
        self.image_url = image_url
        self.offerings = offerings 

# -------------------- Order --------------------

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    passengers = Column(Integer, nullable=False)

    # One-to-One with payment (optional at creation)
    payment = relationship("Payment", back_populates="order")

    user = relationship("User", back_populates="orders")
    trip = relationship("Trip", back_populates="orders")
    def __init__(self, user_id, trip_id, payment_id):
        self.user_id = user_id
        self.trip_id = trip_id
        self.payment_id = payment_id


# -------------------- Payment --------------------

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_id = Column(String, nullable=False)

    user = relationship("User", back_populates="payments")
    order = relationship("Order", back_populates="payment", uselist=False)

    def __init__(self, user_id: int, amount, transaction_id):
        self.user_id = user_id
        self.amount = amount
        self.transaction_id = transaction_id

    
