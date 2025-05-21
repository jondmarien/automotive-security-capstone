from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter

from ....db.mongodb import MongoDB

router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint to verify API and database connectivity.
    """
    # Check database connection
    db_status = "ok"
    try:
        db = MongoDB.get_db()
        await db.command("ping")
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
    }
