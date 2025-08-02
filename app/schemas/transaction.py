# app/schemas/transaction.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class TokenTransfer(BaseModel):
    mint: str
    tokenAmount: float
    fromUserAccount: Optional[str] = None
    toUserAccount: Optional[str] = None
    fromTokenAccount: Optional[str] = None
    toTokenAccount: Optional[str] = None
    tokenStandard: Optional[str] = None

class NativeTransfer(BaseModel):
    fromUserAccount: str
    toUserAccount: str
    amount: int

class TokenBalanceChange(BaseModel):
    userAccount: str
    tokenAccount: str
    rawTokenAmount: Dict[str, Any]
    mint: str

class AccountData(BaseModel):
    account: str
    nativeBalanceChange: int
    tokenBalanceChanges: List[TokenBalanceChange] = []

class Instruction(BaseModel):
    accounts: List[str]
    data: str
    programId: str
    innerInstructions: List[Dict[str, Any]] = []

class JupiterTransaction(BaseModel):
    signature: str
    timestamp: int
    description: Optional[str] = None
    source: Optional[str] = None

class ChildWallet(BaseModel):
    address: str
    amount: float
    timestamp: str

class ParentChildRelationship(BaseModel):
    parent_wallet: str
    child_wallets: List[ChildWallet]
    window_start: str
    unique_recipients_count: int

class ParentChildDetectionResponse(BaseModel):
    wallet_address: Optional[str] = None
    total_transactions: int
    parent_child_relationships: List[ParentChildRelationship]
    detection_params: dict

class RawTransactionResponse(BaseModel):
    wallet_address: Optional[str] = None
    transaction_count: int
    transactions: List[dict]