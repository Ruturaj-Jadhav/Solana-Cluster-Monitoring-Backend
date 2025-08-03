# app/services/helius_service.py
import httpx
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
from app.core.config import settings


SOL_MINT = "So11111111111111111111111111111111111111112"

# Common stablecoins and "buying power" tokens
STABLECOIN_MINTS = {
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",   # USDT
    "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU",   # USDC (Circle)
    "A9mUU4qviSctJVPJdBJWkb28deg915LYJKrzQ19ji3FM",   # USTv2
    "Gz7VkD4MacbEB6yC5XD3HcumEiYx2EtDYYrfikGsvopG",   # wsUSDC
}

# Tokens that represent "buying power" (SOL + stablecoins)
BUYING_POWER_TOKENS = {SOL_MINT} | STABLECOIN_MINTS
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HeliusService:
    def __init__(self):
        self.api_key = settings.HELIUS_API_KEY
        self.base_url = settings.HELIUS_BASE_URL
    
    async def get_raw_transactions(self, wallet_address: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Calls the Helius API to get parsed transactions for a wallet address.
        
        Args:
            wallet_address (str): Solana wallet address
            limit (int): Number of transactions to fetch (max 1000)

        Returns:
            List[Dict[str, Any]]: List of decoded transaction data
        """
        url = f"{self.base_url}/addresses/{wallet_address}/transactions"
        params = {
            "api-key": self.api_key,
            "limit": limit
        }

        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"Making request to: {url}")
                logger.info(f"With params: {params}")
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Successfully fetched {len(data)} transactions for wallet {wallet_address}")
                # Helius might return data in a nested structure
                if isinstance(data, dict) and "result" in data:
                    return data["result"]
                return data
        except httpx.HTTPStatusError as http_err:
            logger.error(f"HTTP error: {http_err.response.status_code} - {http_err.response.text}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch transactions: {str(e)}")
            raise

        return []



    def detect_wallet_clusters(
        self,
        transactions: List[Dict[str, Any]],
        min_children: int = 5,
        funding_window_minutes: int = 5
    ) -> Dict[str, Any]:
        """
        Detect wallet clusters where a parent wallet funds multiple child wallets
        within a short time window, indicating coordinated trading operations.
        
        Args:
            transactions: List of transaction data from Helius
            min_children: Minimum number of children required to form a cluster (default: 5)
            funding_window_minutes: Time window for cluster formation (default: 5 minutes)
            
        Returns:
            Dict containing detected clusters and statistics
        """
        # Step 1: Extract all funding events
        logger.info("Extracting funding events from transactions...")
        funding_events = []
        
        for txn in transactions:
            timestamp = datetime.fromtimestamp(txn["timestamp"])
            
            # Extract token transfers (includes SOL transfers)
            for transfer in txn.get("tokenTransfers", []):
                from_wallet = transfer.get("fromUserAccount")
                to_wallet = transfer.get("toUserAccount")
                amount = float(transfer.get("tokenAmount", 0))
                mint = transfer.get("mint")
                
                if from_wallet and to_wallet and from_wallet != to_wallet and amount > 0:
                    funding_events.append({
                        "parent": from_wallet,
                        "child": to_wallet,
                        "mint": mint,
                        "amount": amount,
                        "timestamp": timestamp,
                        "signature": txn.get("signature")
                    })
        
        # Step 2: Extract all swap events
        logger.info("Extracting swap events from transactions...")
        swap_events = {}  # wallet -> swap_info
        
        for txn in transactions:
            if txn.get("type") == "SWAP":
                timestamp = datetime.fromtimestamp(txn["timestamp"])
                fee_payer = txn.get("feePayer")
                
                if fee_payer and "events" in txn and "swap" in txn["events"]:
                    swap_data = txn["events"]["swap"]
                    
                    # Extract input tokens (what was put into the swap)
                    input_mints = []
                    input_amounts = []
                    for token_input in swap_data.get("tokenInputs", []):
                        if token_input.get("userAccount") == fee_payer:
                            input_mints.append(token_input.get("mint"))
                            raw_amount = token_input.get("rawTokenAmount", {})
                            amount = float(raw_amount.get("tokenAmount", 0))
                            decimals = raw_amount.get("decimals", 0)
                            input_amounts.append(amount / (10 ** decimals))
                    
                    # Extract output tokens (what came out of the swap)
                    output_mints = []
                    for inner_swap in swap_data.get("innerSwaps", []):
                        for token_output in inner_swap.get("tokenOutputs", []):
                            if token_output.get("toUserAccount") == fee_payer:
                                output_mints.append(token_output.get("mint"))
                    
                    swap_events[fee_payer] = {
                        "timestamp": timestamp,
                        "input_mints": input_mints,
                        "output_mints": output_mints,
                        "input_amounts": input_amounts,
                        "signature": txn.get("signature")
                    }
        
        # Step 3: Find funding clusters
        logger.info("Detecting funding clusters...")
        clusters = []
        parent_funding_groups = defaultdict(list)
        
        # Group funding events by parent
        for event in funding_events:
            parent_funding_groups[event["parent"]].append(event)
        
        # Check each parent for cluster formation
        for parent, parent_events in parent_funding_groups.items():
            # Sort events by timestamp
            sorted_events = sorted(parent_events, key=lambda x: x["timestamp"])
            
            # Use sliding window to find clusters
            for i in range(len(sorted_events)):
                window_start = sorted_events[i]["timestamp"]
                window_end = window_start + timedelta(minutes=funding_window_minutes)
                
                # Find all events within this window
                window_events = []
                for j in range(i, len(sorted_events)):
                    if sorted_events[j]["timestamp"] <= window_end:
                        window_events.append(sorted_events[j])
                    else:
                        break
                
                # Check if we have enough children for a cluster
                unique_children = list(set(event["child"] for event in window_events))
                if len(unique_children) >= min_children:
                    
                    # Analyze cluster
                    cluster = self._analyze_cluster(
                        parent, 
                        window_events, 
                        unique_children, 
                        swap_events, 
                        window_start, 
                        window_end
                    )
                    
                    clusters.append(cluster)
                    break  # Found a cluster for this parent, move to next parent
        
        logger.info(f"Found {len(clusters)} wallet clusters")
        
        return {
            "detection_params": {
                "min_children": min_children,
                "funding_window_minutes": funding_window_minutes,
                "total_transactions_analyzed": len(transactions)
            },
            "summary": {
                "clusters_found": len(clusters),
                "total_parents": len([c for c in clusters]),
                "total_children": sum(c["funding_stats"]["children_funded"] for c in clusters),
                "total_children_swapped": sum(c["swap_stats"]["children_swapped"] for c in clusters)
            },
            "clusters": clusters
        }
    
    def _analyze_cluster(
        self, 
        parent: str, 
        funding_events: List[Dict], 
        children: List[str], 
        swap_events: Dict, 
        window_start: datetime, 
        window_end: datetime
    ) -> Dict[str, Any]:
        """
        Analyze a detected cluster to extract detailed statistics.
        """
        # Calculate funding statistics
        total_funding = sum(event["amount"] for event in funding_events)
        funding_token = funding_events[0]["mint"]  # Assume same token for cluster
        
        # Check children swap behavior
        children_data = []
        children_swapped = 0
        total_swap_amount = 0
        target_tokens = set()
        
        for child in children:
            child_funding_events = [e for e in funding_events if e["child"] == child]
            child_funding_amount = sum(e["amount"] for e in child_funding_events)
            
            child_info = {
                "wallet": child,
                "funded_amount": child_funding_amount,
                "swap_status": "pending",
                "swap_amount": 0,
                "swap_time": None,
                "target_tokens": []
            }
            
            # Check if child has swapped
            if child in swap_events:
                swap = swap_events[child]
                # Check if child used the funded token in swap
                if funding_token in swap["input_mints"]:
                    child_info["swap_status"] = "completed"
                    
                    # Find the amount of funded token used
                    for i, mint in enumerate(swap["input_mints"]):
                        if mint == funding_token and i < len(swap["input_amounts"]):
                            child_info["swap_amount"] = swap["input_amounts"][i]
                            total_swap_amount += swap["input_amounts"][i]
                            break
                    
                    child_info["swap_time"] = swap["timestamp"].isoformat()
                    child_info["target_tokens"] = swap["output_mints"]
                    children_swapped += 1
                    target_tokens.update(swap["output_mints"])
            
            children_data.append(child_info)
        
        # Determine cluster type based on funding token
        if funding_token in BUYING_POWER_TOKENS:
            cluster_type = "BUY_CLUSTER"  # SOL or stablecoin funding = buying power
        else:
            cluster_type = "SELL_CLUSTER"  # Specific token funding = likely for selling
        
        return {
            "cluster_id": f"{parent}_{int(window_start.timestamp())}",
            "parent_wallet": parent,
            "formation_time": window_start.isoformat(),
            "formation_window": f"{window_start.isoformat()} - {window_end.isoformat()}",
            "cluster_type": cluster_type,
            
            "funding_stats": {
                "children_funded": len(children),
                "total_amount_sent": round(total_funding, 6),
                "funding_token": funding_token,
                "funding_token_symbol": self._get_token_symbol(funding_token)
            },
            
            "swap_stats": {
                "children_swapped": children_swapped,
                "children_pending": len(children) - children_swapped,
                "total_amount_swapped": round(total_swap_amount, 6),
                "swap_completion_rate": f"{(children_swapped/len(children)*100):.1f}%",
                "target_tokens": list(target_tokens),
                "coordinated_target": len(target_tokens) == 1  # True if all target same token
            },
            
            "children": children_data
        }
    
    def _get_token_symbol(self, mint: str) -> str:
        """
        Get the human-readable symbol for a token mint address.
        """
        token_symbols = {
            "So11111111111111111111111111111111111111112": "SOL",
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC",
            "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": "USDT",
            "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU": "USDC",
            "A9mUU4qviSctJVPJdBJWkb28deg915LYJKrzQ19ji3FM": "USTv2",
            "Gz7VkD4MacbEB6yC5XD3HcumEiYx2EtDYYrfikGsvopG": "wsUSDC"
        }
        return token_symbols.get(mint, "TOKEN")  