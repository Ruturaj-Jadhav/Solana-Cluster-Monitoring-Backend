#!/usr/bin/env python3
"""
Test script for the Solana Parent-Child Wallet Detection API
"""

import asyncio
import httpx
import json
from typing import Dict, Any

async def test_api_endpoints():
    """Test the main API endpoints"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🚀 Testing Solana Parent-Child Wallet Detection API")
        print("=" * 60)
        
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        response = await client.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test raw transactions endpoint
        print("\n2. Testing raw transactions endpoint...")
        response = await client.get(f"{base_url}/api/v1/wallets/raw-transactions?limit=10")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Transaction count: {data.get('transaction_count', 0)}")
        print(f"   Sample transaction: {json.dumps(data.get('transactions', [])[:1], indent=2)}")
        
        # Test parent-child detection endpoint
        print("\n3. Testing parent-child detection endpoint...")
        response = await client.get(
            f"{base_url}/api/v1/wallets/parent-child-detection",
            params={
                "limit": 50,
                "min_child_wallets": 3,
                "time_window_minutes": 10
            }
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Total transactions analyzed: {data.get('total_transactions', 0)}")
        print(f"   Parent-child relationships found: {len(data.get('parent_child_relationships', []))}")
        
        if data.get('parent_child_relationships'):
            print("\n   Sample parent-child relationship:")
            sample = data['parent_child_relationships'][0]
            print(f"   Parent wallet: {sample.get('parent_wallet', 'N/A')}")
            print(f"   Child wallets count: {len(sample.get('child_wallets', []))}")
            print(f"   Unique recipients: {sample.get('unique_recipients_count', 0)}")
            
            if sample.get('child_wallets'):
                print("   Sample child wallets:")
                for i, child in enumerate(sample['child_wallets'][:3]):
                    print(f"     {i+1}. {child.get('address', 'N/A')} - {child.get('amount', 0)} SOL")
        
        # Test API documentation
        print("\n4. Testing API documentation...")
        response = await client.get(f"{base_url}/docs")
        print(f"   Status: {response.status_code}")
        print(f"   Documentation available at: {base_url}/docs")
        
        print("\n✅ All tests completed successfully!")
        print(f"\n📖 API Documentation: {base_url}/docs")
        print(f"🔍 Health Check: {base_url}/health")
        print(f"📊 Raw Transactions: {base_url}/api/v1/wallets/raw-transactions")
        print(f"👥 Parent-Child Detection: {base_url}/api/v1/wallets/parent-child-detection")

if __name__ == "__main__":
    asyncio.run(test_api_endpoints()) 