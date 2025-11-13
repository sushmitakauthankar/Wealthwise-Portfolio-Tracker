from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from apscheduler.schedulers.background import BackgroundScheduler

import models, schemas, crud
from database import engine, SessionLocal

SECRET_KEY = "supersecret123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WealthNest Portfolio Tracker",
    description="Manage portfolios, transactions, and view summaries.",
    version="1.0.0"
)

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = crud.get_user_by_email(db, email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

@app.post("/auth/register", response_model=schemas.UserResponse, tags=["Authentication"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_user(db, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login", tags=["Authentication"])
def login(user: schemas.LoginRequest, db: Session = Depends(get_db)):
    try:
        db_user = crud.authenticate_user(db, user.email, user.password)
        token = create_access_token({"sub": db_user.email})
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/auth/logout", tags=["Authentication"])
def logout():
    return {"message": "Logged out (client should clear token)"}

@app.get("/users/me", response_model=schemas.UserResponse, tags=["Users"])
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.get("/users", response_model=list[schemas.UserResponse], tags=["Users"])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@app.post("/transactions", response_model=dict, tags=["Transactions"])
def create_transaction(tx: schemas.TransactionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    tx.user_id = current_user.id
    new_tx = crud.create_transaction(db, tx)
    return {"message": "Transaction added", "transaction_id": new_tx.id}

@app.get("/transactions", response_model=list[schemas.TransactionResponse], tags=["Transactions"])
def list_transactions(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_transactions(db, current_user.id)

@app.get("/portfolio/summary", response_model=schemas.PortfolioSummaryResponse, tags=["Portfolio"])
def portfolio_summary(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    try:
        return crud.get_portfolio_summary(db, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/prices/{symbol}", tags=["Portfolio"])
def get_price(symbol: str):
    price = crud.get_price(symbol)
    if price is None:
        raise HTTPException(status_code=404, detail="Symbol not found")
    return {"symbol": symbol.upper(), "price": price}

@app.get("/", tags=["Health"])
def root():
    return {"message": "WealthNest API is running"}

scheduler = BackgroundScheduler()
scheduler.add_job(crud.update_prices, "interval", hours=3)
scheduler.start()
print("Background price update scheduler started (every 3 hours)")
