from sqlalchemy import Column, String, Float, Integer, ForeignKey
from app.core.database import Base


class ChildWallet(Base):
    __tablename__ = "child_wallets"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, unique=True, index=True, nullable=False)
    parent_wallet_id = Column(Integer, ForeignKey("parent_wallets.id"), nullable=False)
    sol_received = Column(Float, default=0.0) 