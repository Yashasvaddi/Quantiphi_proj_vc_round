from pydantic import BaseModel, Field


class ConversionRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str

class FavoriteRequest(BaseModel):
    from_currency: str
    to_currency: str

class TravelBudgetRequest(BaseModel):
    base_currency: str
    amount: float = Field(gt=0)
    targets: list[str]