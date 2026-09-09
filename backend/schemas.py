from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from database import Base


class ConversionHistory(Base):

    __tablename__ = "conversion_history"

    id = Column(Integer, primary_key=True, index=True)

    from_currency = Column(String, nullable=False)
    to_currency = Column(String, nullable=False)

    amount = Column(Float, nullable=False)
    converted_amount = Column(Float, nullable=False)

    exchange_rate = Column(Float, nullable=False)

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )


class Favorite(Base):

    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)

    from_currency = Column(String, nullable=False)
    to_currency = Column(String, nullable=False)