from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import get_db
from auth.service import get_current_user
from models import User, Trip
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List 
router = APIRouter()

class CreateTripRequest(BaseModel):
    title: str
    origin: str
    destination: str
    distance_km : int
    start_time : datetime
    end_time: Optional[datetime]
    original_price: float
    discounted_price: float
    slots_left: int
    image_url: str
    offerings : List[str]
@router.post('/add')
async def create_trip(request: Request, trip_request: CreateTripRequest,  db: AsyncSession = Depends(get_db), user: User= Depends(get_current_user)):
    if user.role != 'admin':
        return JSONResponse(status_code=401, content = { 'message': 'only admin can create a trip'})
    stmt = select(Trip).where(Trip.destination == trip_request.destination).where(Trip.origin == trip_request.origin)
    result = await db.execute(stmt)
    trip = result.scalars().first()
    if trip:
        return JSONResponse(status_code=403, content = { 'message ' : f'trip with id: ${trip.id} already exists'})
    trip = Trip(
        title = trip_request.title,
        origin = trip_request.origin,
        destination =  trip_request.destination,
        distance_km = trip_request.distance_km,
        start_time= trip_request.start_time,
        end_time = trip_request.end_time if trip_request.end_time else None,
        original_price  =  trip_request.original_price,
        discounted_price = trip_request.discounted_price,
        slots_left = trip_request.slots_left,
        image_url = trip_request.image_url,
        offerings = trip_request.offerings,
        status="ongoing"
    )
    db.add(trip)
    await db.commit()
    await db.refresh(trip)
    return JSONResponse(status_code = 201, content = {'trip' : { 
        'id': trip.id,
        'title': trip.title,
        'origin': trip.origin,
        'destination' : trip.destination,
        'distance_km': trip.distance_km,
        'start_time': trip.start_time.isoformat(),
        'end_time': trip.end_time.isoformat() if trip.end_time else None,
        'original_price': trip.original_price,
        'discounted_price': trip.discounted_price,
        'slots_left': trip.slots_left,
        'image_url': trip.image_url,
        'status': trip.status
    }})



@router.get('/')
async def get_all_trips(request: Request,  db: AsyncSession = Depends(get_db)):
    stmt = select(Trip)
    result = await db.execute(stmt)
    trips = result.scalars().all()
    print(trips)
    #print(type(trips[0].start_time))
    return JSONResponse(status_code=200, content={
        "trips": [{
            'title': trip.title, 
            'origin': trip.origin,
            'destination': trip.destination,
            'distance_km': trip.distance_km,
            'start_time': trip.start_time.isoformat(),
            'end_time': trip.end_time.isoformat() if trip.end_time else None,
            'original_price': trip.original_price,
            'discounted_price' : trip.discounted_price,
            'status': trip.status,
            'image_url': trip.image_url,
            'slots_left': trip.slots_left,
            'offerings': trip.offerings
        } for trip in trips]
    })

@router.get('/{title}')
async def get_trip_by_title(request: Request, db: AsyncSession = Depends(get_db)):
    title = request.path_params.get('title')
    if not title:
        return JSONResponse(status_code=400, content={ 'message' : 'invalid title'})
    stmt = select(Trip).where(Trip.title == title)
    result = await db.execute(stmt)
    trip = result.scalars().first()
    if not trip:
        return JSONResponse(status_code=400, content={ 'message' : f'trip not found for the given title {title}'})
        
    return JSONResponse(status_code = 201, content = {'trip' : { 
        'id': trip.id,
        'title': trip.title,
        'origin': trip.origin,
        'destination' : trip.destination,
        'distance_km': trip.distance_km,
        'start_time': trip.start_time.isoformat(),
        'end_time': trip.end_time.isoformat() if trip.end_time else None,
        'original_price': trip.original_price,
        'discounted_price': trip.discounted_price,
        'slots_left': trip.slots_left,
        'image_url': trip.image_url,
        'status': trip.status,
        'offerings' : trip.offerings
    }})
    


@router.get('/destinations')
async def get_all_trips(request: Request,  db: AsyncSession = Depends(get_db), user: User= Depends(get_current_user)):
    params = request.query_params
    destination = params.get('destination')
    stmt = select(Trip).where(Trip.destination == destination)
    result = await db.execute(stmt)
    trips = result.scalars().all()
    return JSONResponse(status_code=200, content={
        "trips": [{
            'origin': trip.origin,
            'destination': trip.destination,
            'distance_km': trip.distance_km,
            'start_time': trip.start_time,
            'end_time': trip.end_time,
            'price': trip.price,
            'status': trip.status
        } for trip in trips]
    })
    


