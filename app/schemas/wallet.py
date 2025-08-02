from pydantic import BaseModel
from datetime import datetime
from typing import List


class ChildWallet(BaseModel):
    address: str
    sol_received: float


class ParentWallet(BaseModel):
    address: str
    total_sol_distributed: float
    child_wallet_count: int
    child_wallets: List[ChildWallet] = []


class ParentChildSummary(BaseModel):
    parent_address: str
    total_sol_distributed: float
    child_count: int
    child_addresses: List[str] 