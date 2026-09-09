from pydantic import BaseModel


class ConversionRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str


class FavoriteRequest(BaseModel):
    from_currency: str
    to_currency: str