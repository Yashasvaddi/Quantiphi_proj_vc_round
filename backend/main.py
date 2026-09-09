from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from model import ConversionRequest, FavoriteRequest, TravelBudgetRequest
from exchange_rate import get_exchange_rate
from schemas import ConversionHistory, Favorite
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Query, HTTPException
from datetime import date, timedelta
import httpx
from historical_rates import get_historical_rates

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.post("/history")
def save_history(
    conversion: ConversionRequest,
    converted_amount: float,
    exchange_rate: float,
    db: Session = Depends(get_db)
):

    transaction = ConversionHistory(
        from_currency=conversion.from_currency,
        to_currency=conversion.to_currency,
        amount=conversion.amount,
        converted_amount=converted_amount,
        exchange_rate=exchange_rate
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction

@app.get("/history")
def get_history(
    db: Session = Depends(get_db)
):

    return db.query(
        ConversionHistory
    ).order_by(
        ConversionHistory.timestamp.desc()
    ).all()

@app.post("/favorites")
def add_favorite(
    favorite: FavoriteRequest,
    db: Session = Depends(get_db)
):

    new_favorite = Favorite(
        from_currency=favorite.from_currency,
        to_currency=favorite.to_currency
    )

    db.add(new_favorite)
    db.commit()
    db.refresh(new_favorite)

    return new_favorite

@app.get("/favorites")
def get_favorites(
    db: Session = Depends(get_db)
):

    return db.query(Favorite).all()

@app.delete("/favorites/{favorite_id}")
def delete_favorite(
    favorite_id: int,
    db: Session = Depends(get_db)
):

    favorite = db.query(
        Favorite
    ).filter(
        Favorite.id == favorite_id
    ).first()

    if not favorite:
        return {"error": "Favorite not found"}

    db.delete(favorite)
    db.commit()

    return {"message": "Favorite deleted"}

@app.post("/convert")
async def convert(
    request: ConversionRequest,
    db: Session = Depends(get_db)
):

    rate = await get_exchange_rate(
        request.from_currency,
        request.to_currency
    )

    converted_amount = request.amount * rate

    transaction = ConversionHistory(
        from_currency=request.from_currency,
        to_currency=request.to_currency,
        amount=request.amount,
        converted_amount=converted_amount,
        exchange_rate=rate
    )

    db.add(transaction)
    db.commit()

    return {
        "from": request.from_currency,
        "to": request.to_currency,
        "amount": request.amount,
        "exchange_rate": rate,
        "converted_amount": converted_amount
    }

@app.get("/trend")
async def get_trend(
    from_currency: str = Query(..., alias="from"),
    to_currency: str = Query(..., alias="to"),
    days: int = Query(30, ge=1, le=365)
):
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency == to_currency:
        return {
            "from": from_currency,
            "to": to_currency,
            "days": days,
            "data": [
                {
                    "date": (
                        date.today() - timedelta(days=i)
                    ).isoformat(),
                    "rate": 1.0
                }
                for i in range(days - 1, -1, -1)
            ]
        }

    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    try:
        rates = await get_historical_rates(
            from_currency,
            to_currency,
            start_date.isoformat(),
            end_date.isoformat()
        )

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail="Historical exchange-rate service failed"
        ) from e

    data = [
        {
            "date": row["date"],
            "rate": row["rate"]
        }
        for row in rates
    ]

    return {
        "from": from_currency,
        "to": to_currency,
        "days": days,
        "data": data
    }

@app.post("/travel-budget")
async def travel_budget(
    request: TravelBudgetRequest,
    db: Session = Depends(get_db)
):
    base_currency = request.base_currency.upper()

    results = []

    for target_currency in request.targets:
        target_currency = target_currency.upper()

        try:
            rate = await get_exchange_rate(
                base_currency,
                target_currency
            )

            converted_amount = request.amount * rate

            results.append({
                "currency": target_currency,
                "exchange_rate": rate,
                "converted_amount": converted_amount
            })

        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch rate for {target_currency}"
            ) from e

    return {
        "base_currency": base_currency,
        "amount": request.amount,
        "results": results
    }