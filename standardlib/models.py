from sqlalchemy import Column, Integer
from database import Base


class Helper(Base):
    __tablename__ = "helpers_count"
    DISCORD_ID = Column(Integer, primary_key=True)
    amount_of_times_helped = Column(Integer)

