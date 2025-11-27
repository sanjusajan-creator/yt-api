"""
Comments API Routes
Endpoints for video comments
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from services import client_manager, cache_service

router = APIRouter(prefix="/api/comments", tags=["Comments"])


@router.get("/{video_id}")
async def get_comments(
    video_id: str,
    client: Optional[str] = Query(None, description="Client type")
):
    """
    Get video comments
    
    **Example**: `/api/comments/dQw4w9WgXcQ`
    """
    try:
        params = {"video_id": video_id, "client": client}
        cached = cache_service.get("comments", "comments", params)
        if cached:
            return cached
        
        # Get next data which includes comments
        data = client_manager.next(video_id, client_type=client)
        
        response = {
            "success": True,
            "video_id": video_id,
            "data": data
        }
        
        cache_service.set("comments", "comments", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get comments: {str(e)}")
