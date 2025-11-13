from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TransactionCreate(BaseModel):
    symbol: str
    type: str
    units: float
    price: float
    date: date
    user_id: Optional[int] = None

class TransactionResponse(BaseModel):
    id: int
    symbol: str
    type: str
    units: float
    price: float
    date: date

    class Config:
        from_attributes = True

class Holding(BaseModel):
    symbol: str
    units: float
    avg_cost: float
    current_price: float
    current_value: float
    unrealized_pl: float

class PortfolioSummaryResponse(BaseModel):
    user_id: int
    holdings: list[Holding]
    total_invested: float
    total_value: float
    total_gain: float
