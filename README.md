# Solana Parent-Child Wallet Detection Backend

A FastAPI backend structure for detecting parent-child wallet relationships on the Solana blockchain.

## Project Structure

```
app/
├── core/           # Core configuration and database setup
├── models/         # SQLAlchemy database models (basic structure)
├── schemas/        # Pydantic request/response schemas (basic structure)
├── services/       # Business logic services (basic structure)
└── api/           # FastAPI endpoints (basic structure)
```

## Current Status

This is a **structure-only setup** with:
- ✅ Basic FastAPI application structure
- ✅ Database models for parent and child wallets
- ✅ Service classes for Helius API and wallet detection
- ✅ API endpoint structure
- ❌ No implementation logic yet

## Next Steps

1. **Implement Helius API integration** in `app/services/helius_service.py`
2. **Implement parent-child detection logic** in `app/services/wallet_service.py`
3. **Implement API endpoints** in `app/api/v1/endpoints/wallets.py`
4. **Add database relationships** and proper model methods
5. **Add proper error handling** and validation

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application** (will start but endpoints are empty):
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Planned Features

- Parent-child wallet detection
- SOL distribution tracking
- Real-time monitoring
- RESTful API endpoints 