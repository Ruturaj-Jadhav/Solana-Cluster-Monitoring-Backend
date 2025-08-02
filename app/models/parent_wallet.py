from sqlalchemy import Column, String, Float, Integer
from app.core.database import Base


class ParentWallet(Base):
    __tablename__ = "parent_wallets"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, unique=True, index=True, nullable=False)
    total_sol_distributed = Column(Float, default=0.0)
    child_wallet_count = Column(Integer, default=0) 