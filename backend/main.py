from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from model import ConversionRequest, FavoriteRequest
from exchange_rate import get_exchange_rate
from schemas import ConversionHistory, Favorite
from fastapi.middleware.cors import CORSMiddleware

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