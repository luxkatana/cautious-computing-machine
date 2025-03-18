from sqlalchemy import Column, Integer
from . import database



class Helper(database.Base):
    __tablename__ = "helpers_count"
    DISCORD_ID = Column(Integer, primary_key=True)
    amount_of_times_helped = Column(Integer)

