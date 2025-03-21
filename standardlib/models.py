from sqlalchemy import Column, BigInteger, Integer
try:
    from standardlib.database import Base
except Exception:
    from database import Base



class Helper(Base):
    __tablename__ = "helpers_count"
    DISCORD_ID = Column(BigInteger, primary_key=True)
    amount_of_times_helped = Column(Integer)

