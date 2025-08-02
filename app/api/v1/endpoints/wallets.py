# app/api/v1/endpoints/wallets.py
from fastapi import APIRouter, HTTPException, Path, Query
from typing import Dict, Any
import logging
from app.services.helius_service import HeliusService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()
helius_service = HeliusService()


@router.get("/raw-transactions/{wallet_address}")
async def get_raw_transactions(
    wallet_address: str = Path(..., description="Solana wallet address"),
) -> Dict[str, Any]:
    """
    Get raw transactions for a specific Solana wallet address.
    
    Args:
        wallet_address: The Solana wallet address to fetch transactions for
    
    Returns:
        Any response format - completely flexible
    """
    try:
        logger.info(f"Fetching raw transactions for wallet: {wallet_address}")
    
        # # Call the Helius service to get raw transactions
        transactions = await helius_service.get_raw_transactions(wallet_address, 100)
    
        # Return the response using the schema
        return {"transactions": transactions}
        
    except Exception as e:
        logger.error(f"Error fetching raw transactions for wallet {wallet_address}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch raw transactions: {str(e)}"
        )

@router.get("/parent-child-wallets/{wallet_address}")
async def get_parent_child_wallets(
    wallet_address: str = Path(..., description="Solana wallet address"),
) -> Dict[str, Any]:
    """
    Get parent-child wallets for a specific Solana wallet address.
    """
    try:
        logger.info(f"Fetching parent-child wallets for wallet: {wallet_address}")
        transactions = await helius_service.get_raw_transactions(wallet_address, 100)
        parent_child_wallets = helius_service.detect_parent_child_wallets(transactions, 5, 5)
        return {"parent_child_wallets": parent_child_wallets}
    except Exception as e:
        logger.error(f"Error fetching parent-child wallets for wallet {wallet_address}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch parent-child wallets: {str(e)}")

@router.get("/cluster-detection/{wallet_address}")
async def get_cluster_detection(
    wallet_address: str = Path(..., description="Solana wallet address"),
    min_children: int = Query(default=5, ge=3, le=20, description="Minimum children required for cluster (3-20)"),
    funding_window: int = Query(default=5, ge=1, le=30, description="Funding window in minutes for cluster formation (1-30)")
) -> Dict[str, Any]:
    """
    Detect wallet clusters where a parent wallet funds multiple child wallets
    within a short time window, indicating coordinated trading operations.
    
    This cluster detection looks for:
    - Parent wallet funding ≥5 child wallets within 5-minute window
    - Child wallets may perform swaps (tracked but no time constraint)
    - Clusters classified as BUY_CLUSTER (SOL funding) or SELL_CLUSTER (token funding)
    - Coordination detection (all children targeting same token)
    """
    try:
        logger.info(f"Detecting wallet clusters for: {wallet_address}, min_children: {min_children}, window: {funding_window}min")
        transactions = await helius_service.get_raw_transactions(wallet_address, 100)
        cluster_analysis = helius_service.detect_wallet_clusters(transactions, min_children, funding_window)
        return cluster_analysis
    except Exception as e:
        logger.error(f"Error detecting wallet clusters for {wallet_address}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to detect wallet clusters: {str(e)}")

