WealthWise Portfolio Tracker — Backend (FastAPI + PostgreSQL)
-----------------------------------------------------------------------------------------------------------------------------------------------------------------
A backend service that allows users to track their stock/mutual-fund investments, maintain holdings, and compute portfolio returns using mock market price data.

Features:
----------
1)Authentication

2)Register new users

3)Secure login (JWT Bearer token)

4)Protected endpoints (transactions, portfolio summary)

💹 Portfolio Tracking
-----------------------
Add BUY / SELL transactions

View full transaction history

Auto-calculate:

-Holdings

-Weighted average cost

-Current value

-Unrealized P/L

-Total invested value

-Overall portfolio gain/loss

📊 Price Handling
-------------------
Prices stored locally in prices.json

Prices also stored in PostgreSQL (prices table)

Background scheduler updates DB prices every 3 hours

🛢 Persistence
---------------
Fully integrated with PostgreSQL

Models:
-users

-transactions

-prices

🧑‍💻 Setup Instructions
-----------------------
1️⃣ Clone the Repository :

git clone https://github.com/sushmitakauthankar/WealthWise-Portfolio-Tracker.git

cd WealthWise-Portfolio-Tracker

2️⃣ Create Virtual Environment :

python -m venv venv

venv\Scripts\activate

3️⃣ Install Dependencies :

pip install -r requirements.txt

4️⃣ Set Up PostgreSQL :

Create a new database: CREATE DATABASE wealthnest;

Update DB credentials in database.py if needed:

DB_USER = "postgres"

DB_PASSWORD = "your_password"

DB_HOST = "localhost"

DB_NAME = "wealthnest"

Tables will auto-create on running the app.

5️⃣ Run the Application

uvicorn main:app --reload

The API will be available at: http://127.0.0.1:8000

Swagger Docs: http://127.0.0.1:8000/docs

Authentication Flow
--------------------
1. Register
   
POST /auth/register

example :
 {
  "name": "Sushmita",  
    "email": "sushmita@example.com",
    "password": "123"
}

2. Login
   
POST /auth/login

example :
{
  "email": "sushmita@example.com",
    "password": "123"
}

Response:
{
  "access_token": "JWT_TOKEN_HERE",
    "token_type": "bearer"
}

3. Authorize in Swagger

Click 🔒 Authorize

Paste the token and authorize

4. Transactions

POST	/transactions/	Add BUY/SELL transaction

GET	/transactions/	View user's transaction history

Example :

{
  "symbol": "TCS",
    "type": "BUY",
    "units": 5,
    "price": 3200,
    "date": "2025-05-10"
}

5. Portfolio Summary

GET /portfolio-summary

Example:

{
  "user_id": 1,
  "holdings": [
    {
      "symbol": "TCS",
      "units": 5,
      "avg_cost": 3200,
      "current_price": 3400,
      "current_value": 17000,
      "unrealized_pl": 1000
    }
  ],
  "total_invested": 16000,
  "total_value": 17000,
  "total_gain": 1000
}

