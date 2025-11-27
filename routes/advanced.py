"""
Advanced API Routes
Batch requests, captions, analytics, and other advanced features
"""
from fastapi import APIRouter, Query, HTTPException, Body
from typing import Optional, List, Dict, Any
from services import client_manager, cache_service
import asyncio

router = APIRouter(prefix="/api", tags=["Advanced Features"])


@router.post("/batch")
async def batch_request(
    requests: List[Dict[str, Any]] = Body(..., description="List of requests to execute")
):
    """
    Execute multiple requests in one call
    
    **Example**:
    ```json
    [
        {"endpoint": "search", "params": {"query": "python"}},
        {"endpoint": "video", "params": {"video_id": "dQw4w9WgXcQ"}}
    ]
    ```
    """
    try:
        if len(requests) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 requests allowed in batch")
        
        results = []
        
        for req in requests:
            endpoint = req.get("endpoint")
            params = req.get("params", {})
            
            try:
                if endpoint == "search":
                    result = client_manager.search(**params)
                elif endpoint == "video":
                    result = client_manager.player(**params)
                elif endpoint == "browse":
                    result = client_manager.browse(**params)
                elif endpoint == "next":
                    result = client_manager.next(**params)
                else:
                    result = {"error": f"Unknown endpoint: {endpoint}"}
                
                results.append({
                    "success": True,
                    "endpoint": endpoint,
                    "data": result
                })
            except Exception as e:
                results.append({
                    "success": False,
                    "endpoint": endpoint,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch request failed: {str(e)}")


@router.get("/captions/{video_id}")
async def get_captions(
    video_id: str,
    client: Optional[str] = Query(None, description="Client type")
):
    """
    Get video captions/subtitles
    
    **Example**: `/api/captions/dQw4w9WgXcQ`
    """
    try:
        params = {"video_id": video_id, "client": client}
        cached = cache_service.get("default", "captions", params)
        if cached:
            return cached
        
        # Get player data which includes caption tracks
        data = client_manager.player(video_id, client_type=client)
        
        captions = data.get("captions", {})
        
        response = {
            "success": True,
            "video_id": video_id,
            "captions": captions
        }
        
        cache_service.set("default", "captions", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get captions: {str(e)}")


@router.get("/livestream/{video_id}")
async def get_livestream(
    video_id: str,
    client: Optional[str] = Query(None, description="Client type")
):
    """
    Get live stream information
    
    **Example**: `/api/livestream/jfKfPfyJRdk`
    """
    try:
        params = {"video_id": video_id, "client": client}
        cached = cache_service.get("default", "livestream", params)
        if cached:
            return cached
        
        player_data = client_manager.player(video_id, client_type=client)
        
        video_details = player_data.get("videoDetails", {})
        is_live = video_details.get("isLiveContent", False)
        
        response = {
            "success": True,
            "video_id": video_id,
            "is_live": is_live,
            "video_details": video_details,
            "streaming_data": player_data.get("streamingData", {})
        }
        
        cache_service.set("default", "livestream", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get livestream info: {str(e)}")


@router.get("/shorts/{shorts_id}")
async def get_shorts(
    shorts_id: str,
    client: Optional[str] = Query(None, description="Client type")
):
    """
    Get YouTube Shorts data
    
    **Example**: `/api/shorts/abc123`
    """
    try:
        params = {"shorts_id": shorts_id, "client": client}
        cached = cache_service.get("default", "shorts", params)
        if cached:
            return cached
        
        # Shorts are essentially videos
        data = client_manager.player(shorts_id, client_type=client)
        
        response = {
            "success": True,
            "shorts_id": shorts_id,
            "data": data
        }
        
        cache_service.set("default", "shorts", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get shorts: {str(e)}")


@router.get("/analytics")
async def get_analytics():
    """
    Get API usage analytics and cache statistics
    
    **Example**: `/api/analytics`
    """
    try:
        stats = cache_service.get_stats()
        
        return {
            "success": True,
            "cache_stats": stats,
            "api_info": {
                "version": "1.0.0",
                "endpoints": "50+",
                "features": [
                    "YouTube Search",
                    "Video Information",
                    "Channel Data",
                    "Playlists",
                    "Comments",
                    "YouTube Music",
                    "Batch Requests",
                    "Captions",
                    "Live Streams",
                    "Shorts"
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")


@router.post("/cache/clear")
async def clear_cache(
    cache_type: Optional[str] = Query(None, description="Cache type to clear (or all)")
):
    """
    Clear API cache
    
    **Example**: `/api/cache/clear?cache_type=search`
    """
    try:
        cache_service.clear(cache_type)
        
        return {
            "success": True,
            "message": f"Cleared {cache_type if cache_type else 'all'} cache(s)"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")
