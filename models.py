from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, nullable=False)
    type = Column(String, nullable=False)  # BUY / SELL
    units = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    date = Column(Date, nullable=False)

    user = relationship("User", back_populates="transactions")


class Price(Base):
    __tablename__ = "prices"
    symbol = Column(String, primary_key=True)
    price = Column(Float, nullable=False)
