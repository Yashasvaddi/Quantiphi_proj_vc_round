# Currency Converter

A full-stack currency conversion web application built with **FastAPI, SQLite, HTML/CSS/JavaScript, and external exchange-rate APIs**.

The application supports real-time currency conversion, 30-day exchange-rate trends, favorite currency pairs, persistent conversion history, and a Travel Budgeting mode.

The FastAPI backend also serves the frontend, allowing the complete application to be deployed as a single service on platforms such as Render.

---

## Features

### 💱 Currency Converter

- Select a source currency and target currency.
- Enter an amount to convert.
- Fetches the current exchange rate from the ExchangeRate API.
- Performs the conversion calculation on the backend.
- Stores successful conversions in SQLite.
- Displays the converted amount and exchange rate in the frontend.

### 📈 30-Day Exchange Rate Trend

- Displays historical exchange-rate data for the selected currency pair.
- Uses historical exchange-rate data from the Frankfurter API.
- Renders the returned data as a line chart using Chart.js.
- Historical data retrieval is handled by the backend.

### ⭐ Favorites

- Add frequently used currency pairs to favorites.
- View saved currency pairs.
- Delete favorites.
- Favorites persist in SQLite.

### 🗄️ Conversion History

Every successful conversion is stored in SQLite with:

- Source currency
- Target currency
- Amount
- Converted amount
- Exchange rate
- Timestamp

### ✈️ Travel Budgeting

- Enter a base currency and amount.
- Backend calculates the equivalent amount in five major currencies.
- Results are returned through the API.
- Frontend displays the results in a comparison table.
- Favorite currency pairs can be highlighted.

### 🌐 Single-Service Deployment

FastAPI serves both:

- Backend API endpoints
- Frontend `index.html`

This means the application can be deployed as one Render Web Service.

---

# Architecture

```text
                         ┌─────────────────────┐
                         │      Browser        │
                         │ HTML/CSS/JavaScript │
                         └──────────┬──────────┘
                                    │
                                    │ HTTP
                                    ▼
                         ┌─────────────────────┐
                         │       FastAPI       │
                         │      Backend        │
                         └──────┬───────┬──────┘
                                │       │
                   ┌────────────┘       └─────────────┐
                   ▼                                  ▼
        ┌─────────────────────┐             ┌──────────────────┐
        │ ExchangeRate API    │             │ SQLite Database  │
        │ Current Rates       │             │                  │
        └─────────────────────┘             │ History          │
                                             │ Favorites        │
                                             └──────────────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │  Frankfurter API    │
                     │ Historical Rates    │
                     └─────────────────────┘
```

---

# Project Structure

```text
currency-converter/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── model.py
│   ├── schemas.py
│   ├── exchange_rate.py
│   └── historical_rates.py
│
├── frontend/
│   └── index.html
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

### Backend responsibilities

| File | Responsibility |
|---|---|
| `main.py` | FastAPI application, routes, frontend serving |
| `database.py` | SQLAlchemy engine and database sessions |
| `model.py` | SQLite/SQLAlchemy database models |
| `schemas.py` | Request validation schemas |
| `exchange_rate.py` | Current exchange-rate API integration |
| `historical_rates.py` | Historical exchange-rate API integration |

---

# Tech Stack

## Frontend

- HTML5
- CSS3
- JavaScript
- Chart.js

## Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- HTTPX
- python-dotenv

## External APIs

- **ExchangeRate API** — current exchange rates
- **Frankfurter API** — historical exchange rates

---

# API Endpoints

## `GET /`

Serves the frontend application.

```text
GET /
```

FastAPI returns:

```text
frontend/index.html
```

This allows the frontend and backend to run from the same server.

---

## `POST /convert`

Converts an amount between two currencies.

### Request

```json
{
  "from_currency": "USD",
  "to_currency": "EUR",
  "amount": 100
}
```

### Response

```json
{
  "from": "USD",
  "to": "EUR",
  "amount": 100,
  "exchange_rate": 0.85,
  "converted_amount": 85
}
```

A successful conversion is also saved to the conversion-history table.

---

## `GET /history`

Returns stored conversion history.

```text
GET /history
```

The newest conversion records are returned first.

---

## `GET /favorites`

Returns saved favorite currency pairs.

```text
GET /favorites
```

---

## `POST /favorites`

Adds a currency pair to favorites.

### Request

```json
{
  "from_currency": "USD",
  "to_currency": "EUR"
}
```

---

## `DELETE /favorites/{id}`

Deletes a favorite.

```text
DELETE /favorites/1
```

---

## `GET /trend`

Returns historical exchange-rate data.

Example:

```text
GET /trend?from=USD&to=EUR&days=30
```

### Response

```json
{
  "from": "USD",
  "to": "EUR",
  "days": 30,
  "data": [
    {
      "date": "2026-08-11",
      "rate": 0.85
    }
  ]
}
```

---

## `POST /travel-budget`

Calculates the equivalent value of an amount across five major currencies.

### Request

```json
{
  "from_currency": "USD",
  "amount": 1000
}
```

The backend performs the required exchange-rate calculations and returns the results for display in the comparison table.

---

# Database

SQLite is used for persistent application data.

## Conversion History

The `conversion_history` table contains:

```text
id
from_currency
to_currency
amount
converted_amount
exchange_rate
timestamp
```

## Favorites

The `favorites` table contains:

```text
id
from_currency
to_currency
```

SQLite is used for **persistent history and favorites**.

It is not treated as the authoritative source for current exchange rates. Current conversion requests retrieve live rate information from the external exchange-rate service.

---

# Exchange Rate Strategy

The application separates **current rates** from **historical rates**.

### Current conversion

```text
Frontend
   ↓
POST /convert
   ↓
FastAPI
   ↓
ExchangeRate API
   ↓
Current exchange rate
   ↓
Backend calculation
   ↓
SQLite history + API response
```

The backend calculates:

```text
converted_amount = amount × exchange_rate
```

### Historical trend

```text
Frontend
   ↓
GET /trend
   ↓
FastAPI
   ↓
Frankfurter API
   ↓
Historical rates
   ↓
Frontend chart
```

There is no background job continuously downloading exchange rates.

A current exchange rate is fetched when a conversion request is made.

---

# Server-Side Business Logic

Business logic and calculations are intentionally handled by the backend.

The frontend primarily handles:

- User interaction
- Form inputs
- API requests
- Rendering results
- Chart rendering
- UI state

The backend handles:

- Request validation
- Exchange-rate retrieval
- Currency conversion calculations
- Travel Budget calculations
- Database persistence
- Historical-rate retrieval
- API error handling

This keeps the business rules centralized and prevents the frontend from being the source of truth for financial calculations.

---

# Frontend ↔ Backend Configuration

Because FastAPI serves the frontend, the frontend can use relative API paths.

For example:

```javascript
const BASE_URL = "";

fetch(`${BASE_URL}/convert`);
```

This becomes:

```text
/convert
```

rather than hard-coding:

```text
http://127.0.0.1:8000
```

This is important for deployment because the same frontend code works locally and on Render.

---

# Environment Variables

Create a `.env` file:

```env
EXCHANGE_RATE_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./currency.db
```

### Important

Never commit the actual API key to GitHub.

Add the following to `.gitignore`:

```gitignore
.env
*.db
__pycache__/
.venv/
```

---

# Local Setup

## 1. Clone the repository

```bash
git clone <your-repository-url>
cd <repository-directory>
```

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` has not been created yet:

```bash
pip install fastapi uvicorn sqlalchemy httpx python-dotenv
```

## 4. Configure `.env`

```env
EXCHANGE_RATE_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./currency.db
```

---

# Running Locally

Start the FastAPI server:

```bash
uvicorn backend.main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

Open:

```text
http://127.0.0.1:8000/
```

FastAPI API documentation:

```text
http://127.0.0.1:8000/docs
```

Because FastAPI serves the frontend, there is no need to run a separate frontend server.

---

# Render Deployment

The application is designed to run as a single Render Web Service.

## Build Command

```bash
pip install -r requirements.txt
```

## Start Command

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Render automatically provides the `$PORT` environment variable.

## Environment Variables on Render

Configure:

```text
EXCHANGE_RATE_API_KEY = your_api_key
DATABASE_URL = sqlite:///./currency.db
```

After deployment:

```text
https://your-app-name.onrender.com/
```

serves the frontend.

API endpoints are available under the same domain:

```text
https://your-app-name.onrender.com/convert
https://your-app-name.onrender.com/history
https://your-app-name.onrender.com/favorites
https://your-app-name.onrender.com/trend
https://your-app-name.onrender.com/travel-budget
```

---

# FastAPI Frontend Serving

The frontend is served using `FileResponse`.

The relevant backend setup is:

```python
from pathlib import Path
from fastapi.responses import FileResponse

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")
```

Using `Path(__file__)` makes the frontend path independent of the directory from which Uvicorn is started.

---

# Data Flow

## Currency Conversion

```text
User enters amount
        ↓
Frontend sends POST /convert
        ↓
FastAPI validates request
        ↓
Backend requests current rate
        ↓
ExchangeRate API
        ↓
Backend calculates converted amount
        ↓
Conversion saved to SQLite
        ↓
Response returned to frontend
        ↓
UI displays result
```

## Favorites

```text
User clicks Favorite
        ↓
POST /favorites
        ↓
FastAPI
        ↓
SQLite
        ↓
Favorite persisted
        ↓
Frontend refreshes favorites
```

## Travel Budget

```text
User enters base amount
        ↓
POST /travel-budget
        ↓
FastAPI
        ↓
Exchange rates retrieved
        ↓
Backend calculates five results
        ↓
JSON response
        ↓
Frontend renders comparison table
```

---

# Validation and Error Handling

Validation should be performed on the backend so that API consumers cannot bypass frontend validation.

Expected validation includes:

- Valid currency codes
- Uppercase currency normalization
- Positive conversion amounts
- Positive Travel Budget amounts
- Valid source and target currencies
- Valid trend-day ranges

External API failures should be converted into appropriate backend HTTP errors rather than exposing raw provider errors to the frontend.

---

# Security Considerations

### API Key

The ExchangeRate API key is stored in:

```text
.env
```

and accessed by the backend.

It is never exposed to frontend JavaScript.

### CORS

For local development, permissive CORS may be used.

For production, CORS should ideally be restricted to the deployed frontend origin.

### Secrets

Do not commit:

```text
.env
```

to GitHub.

---

# Testing Checklist

Before deployment/submission:

- [ ] Frontend opens through `GET /`.
- [ ] USD → EUR conversion works.
- [ ] Currency selection works.
- [ ] Amount changes trigger conversion.
- [ ] Backend performs conversion calculation.
- [ ] Invalid amounts are rejected.
- [ ] Invalid currency codes are rejected.
- [ ] Conversion history is stored in SQLite.
- [ ] `/history` returns saved conversions.
- [ ] Favorites can be added.
- [ ] Favorites can be deleted.
- [ ] Duplicate favorites are handled correctly.
- [ ] 30-day trend loads.
- [ ] Trend works for different currency pairs.
- [ ] Travel Budgeting returns five currencies.
- [ ] Travel Budgeting table renders backend results.
- [ ] API failures are handled gracefully.
- [ ] `.env` is excluded from Git.
- [ ] No mock/fake exchange-rate fallback remains.
- [ ] Render deployment starts successfully.
- [ ] Render frontend loads from `/`.
- [ ] API calls use relative paths.
- [ ] GitHub repository is configured as required by the assessment.

---

# Assessment Requirement Mapping

| Requirement | Implementation |
|---|---|
| Currency conversion | FastAPI `/convert` + ExchangeRate API |
| Live exchange-rate data | ExchangeRate API |
| 30-day trend | `/trend` + Frankfurter + Chart.js |
| Favorites | SQLite + `/favorites` endpoints |
| Conversion history | SQLite + `/history` |
| Travel Budgeting | `/travel-budget` |
| Server-side calculations | FastAPI backend |
| Server-side validation | FastAPI/Pydantic |
| Persistent storage | SQLite |
| Frontend rendering | FastAPI `GET /` |
| Deployment | Render Web Service |

---

# Design Decisions

## Why FastAPI serves the frontend

Serving the frontend directly from FastAPI allows the application to be deployed as one service.

Instead of:

```text
Frontend Server → Backend Server
```

the deployment becomes:

```text
Render
  │
  └── FastAPI
       ├── Frontend
       └── API
```

This simplifies deployment and eliminates the need to configure a separate frontend service.

## Why current rates are fetched on conversion

The application requires live conversion data. Therefore, the backend requests the current rate when a conversion is made instead of treating an old SQLite record as the current rate.

SQLite remains responsible for persistent application data such as history and favorites.

## Why historical rates use a separate provider

Current conversion rates and historical time-series data are separate API requirements.

The application therefore uses:

- ExchangeRate API for current conversion rates.
- Frankfurter for historical trend data.

---

# Future Improvements

Possible production improvements include:

- User authentication
- Per-user favorites and history
- Database uniqueness constraint for favorite pairs
- Automated backend tests with `pytest`
- External API retry/backoff
- Rate-limit handling
- Rate caching with an explicit freshness policy
- Restricted CORS
- PostgreSQL for production persistence
- Docker-based deployment
- Better structured API response/error models
- Health-check endpoint such as `/health`

---

# License

This project was developed as part of a technical assessment.
