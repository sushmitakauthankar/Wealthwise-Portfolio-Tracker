from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models, schemas, json, os
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
PRICES_FILE = os.path.join(os.path.dirname(__file__), "prices.json")

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    if get_user_by_email(db, user.email):
        raise Exception("Email already registered")

    clean_pw = user.password.encode("utf-8")[:72].decode("utf-8", "ignore")
    hashed = pwd_context.hash(clean_pw)
    new_user = models.User(name=user.name, email=user.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def authenticate_user(db: Session, email: str, password: str) -> models.User:
    user = get_user_by_email(db, email)
    if not user:
        raise Exception("Invalid credentials")
    clean_pw = password.encode("utf-8")[:72].decode("utf-8", "ignore")
    if not pwd_context.verify(clean_pw, user.hashed_password):
        raise Exception("Invalid credentials")
    return user

def create_transaction(db: Session, tx: schemas.TransactionCreate) -> models.Transaction:
    db_tx = models.Transaction(
        user_id=tx.user_id,
        symbol=tx.symbol.upper(),
        type=tx.type.upper(),
        units=tx.units,
        price=tx.price,
        date=tx.date
    )
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx

def get_transactions(db: Session, user_id: int):
    return db.query(models.Transaction).filter(models.Transaction.user_id == user_id).order_by(models.Transaction.date).all()

def get_price(symbol: str) -> Optional[float]:
    try:
        with open(PRICES_FILE, "r") as f:
            data = json.load(f)
        return data.get(symbol.upper())
    except Exception:
        return None

def load_prices_from_json_to_db(db: Session):

    from sqlalchemy import insert
    try:
        with open(PRICES_FILE, "r") as f:
            data = json.load(f)
        for symbol, price in data.items():

            obj = db.query(models.Price).filter(models.Price.symbol == symbol).first()
            if obj:
                obj.price = price
            else:
                p = models.Price(symbol=symbol, price=price)
                db.add(p)
        db.commit()
        return True
    except Exception:
        return False

def update_prices():
    try:
        with open(PRICES_FILE, "r") as f:
            data = json.load(f)

        for symbol in list(data.keys()):
            data[symbol] = round(data[symbol] * 1.01, 2)
        with open(PRICES_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print("Prices updated (mock).")
    except Exception as e:
        print("Price update failed:", e)

def get_portfolio_summary(db: Session, user_id: int):
    txs = get_transactions(db, user_id)
    if not txs:
        return {
            "user_id": user_id,
            "holdings": [],
            "total_invested": 0.0,
            "total_value": 0.0,
            "total_gain": 0.0
        }

    portfolio = {}
    for tx in txs:
        sym = tx.symbol.upper()
        if sym not in portfolio:
            portfolio[sym] = {"units": 0.0, "cost": 0.0, "buy_units": 0.0, "buy_amount": 0.0}
        if tx.type.upper() == "BUY":
            portfolio[sym]["units"] += tx.units
            portfolio[sym]["cost"] += tx.units * tx.price
            portfolio[sym]["buy_units"] += tx.units
            portfolio[sym]["buy_amount"] += tx.units * tx.price
        elif tx.type.upper() == "SELL":

            if portfolio[sym]["units"] <= 0:

                portfolio[sym]["units"] -= tx.units
            else:

                avg_cost = portfolio[sym]["cost"] / portfolio[sym]["units"] if portfolio[sym]["units"] else 0
                portfolio[sym]["units"] -= tx.units
                portfolio[sym]["cost"] -= avg_cost * tx.units

    holdings = []
    total_invested = 0.0
    total_value = 0.0
    for sym, data in portfolio.items():
        units = round(data["units"], 6)
        if units <= 0:
            continue
        avg_cost = (data["cost"] / units) if units else 0.0
        current_price = get_price(sym) or 0.0
        current_value = round(units * current_price, 2)
        invested = round(units * avg_cost, 2)
        unrealized = round(current_value - invested, 2)

        holdings.append({
            "symbol": sym,
            "units": units,
            "avg_cost": round(avg_cost, 2),
            "current_price": round(current_price, 2),
            "current_value": current_value,
            "unrealized_pl": unrealized
        })

        total_invested += invested
        total_value += current_value

    total_gain = round(total_value - total_invested, 2)

    return {
        "user_id": user_id,
        "holdings": holdings,
        "total_invested": round(total_invested, 2),
        "total_value": round(total_value, 2),
        "total_gain": total_gain
    }
