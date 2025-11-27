"""
YouTube API Routes
Core YouTube endpoints for search, video, browse, trending
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any
from services import client_manager, cache_service
from utils import extract_contents, parse_video_renderer

router = APIRouter(prefix="/api", tags=["YouTube"])


@router.get("/search")
async def search(
    query: str = Query(..., description="Search query"),
    client: Optional[str] = Query(None, description="Client type (WEB, ANDROID, etc.)"),
    limit: Optional[int] = Query(20, description="Maximum number of results"),
    filter: Optional[str] = Query(None, description="Filter (video, channel, playlist)")
):
    """
    Search YouTube for videos, channels, and playlists
    
    **Example**: `/api/search?query=python+tutorial&limit=10`
    """
    try:
        # Check cache
        params = {"query": query, "client": client, "limit": limit, "filter": filter}
        cached = cache_service.get("search", "search", params)
        if cached:
            return cached
        
        # Execute search
        data = client_manager.search(query, client_type=client)
        
        # Parse results
        results = extract_contents(data, renderer_type="video")
        
        # Apply limit
        if limit:
            results = results[:limit]
        
        response = {
            "success": True,
            "query": query,
            "count": len(results),
            "results": results,
            "raw_data": data  # Include raw data for power users
        }
        
        # Cache response
        cache_service.set("search", "search", params, response)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/video/{video_id}")
async def get_video(
    video_id: str,
    client: Optional[str] = Query(None, description="Client type")
):
    """
    Get detailed video information
    
    **Example**: `/api/video/dQw4w9WgXcQ`
    """
    try:
        # Check cache
        params = {"video_id": video_id, "client": client}
        cached = cache_service.get("video", "video", params)
        if cached:
            return cached
        
        # Get video data
        player_data = client_manager.player(video_id, client_type=client)
        next_data = client_manager.next(video_id, client_type=client)
        
        # Extract video details
        video_details = player_data.get("videoDetails", {})
        
        response = {
            "success": True,
            "video_id": video_id,
            "title": video_details.get("title", ""),
            "author": video_details.get("author", ""),
            "length_seconds": video_details.get("lengthSeconds", ""),
            "view_count": video_details.get("viewCount", ""),
            "short_description": video_details.get("shortDescription", ""),
            "is_live": video_details.get("isLiveContent", False),
            "channel_id": video_details.get("channelId", ""),
            "thumbnails": video_details.get("thumbnail", {}).get("thumbnails", []),
            "keywords": video_details.get("keywords", []),
            "rating": video_details.get("averageRating", 0),
            "player_data": player_data,
            "related_videos": next_data
        }
        
        # Cache response
        cache_service.set("video", "video", params, response)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get video: {str(e)}")


@router.get("/player/{video_id}")
async def get_player(
    video_id: str,
    client: Optional[str] = Query(None, description="Client type")
):
    """
    Get video streaming data and available formats
    
    **Example**: `/api/player/dQw4w9WgXcQ`
    """
    try:
        params = {"video_id": video_id, "client": client}
        cached = cache_service.get("video", "player", params)
        if cached:
            return cached
        
        data = client_manager.player(video_id, client_type=client)
        
        response = {
            "success": True,
            "video_id": video_id,
            "streaming_data": data.get("streamingData", {}),
            "video_details": data.get("videoDetails", {}),
            "playability_status": data.get("playabilityStatus", {}),
            "raw_data": data
        }
        
        cache_service.set("video", "player", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get player data: {str(e)}")


@router.get("/next/{video_id}")
async def get_next(
    video_id: str,
    client: Optional[str] = Query(None, description="Client type")
):
    """
    Get related videos and recommendations
    
    **Example**: `/api/next/dQw4w9WgXcQ`
    """
    try:
        params = {"video_id": video_id, "client": client}
        cached = cache_service.get("video", "next", params)
        if cached:
            return cached
        
        data = client_manager.next(video_id, client_type=client)
        
        response = {
            "success": True,
            "video_id": video_id,
            "data": data
        }
        
        cache_service.set("video", "next", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get related videos: {str(e)}")


@router.get("/browse/{browse_id}")
async def browse(
    browse_id: str,
    client: Optional[str] = Query(None, description="Client type")
):
    """
    Browse any YouTube page by ID
    
    **Example**: `/api/browse/FEwhat_to_watch`
    """
    try:
        params = {"browse_id": browse_id, "client": client}
        cached = cache_service.get("default", "browse", params)
        if cached:
            return cached
        
        data = client_manager.browse(browse_id, client_type=client)
        
        response = {
            "success": True,
            "browse_id": browse_id,
            "data": data
        }
        
        cache_service.set("default", "browse", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to browse: {str(e)}")


@router.get("/trending")
async def get_trending(
    region: Optional[str] = Query("US", description="Region code (US, GB, etc.)"),
    client: Optional[str] = Query(None, description="Client type")
):
    """
    Get trending videos
    
    **Example**: `/api/trending?region=US`
    """
    try:
        params = {"region": region, "client": client}
        cached = cache_service.get("trending", "trending", params)
        if cached:
            return cached
        
        # Browse trending page (Force ANDROID client if not specified, as WEB often fails)
        target_client = client or "ANDROID"
        data = client_manager.browse("FEtrending", client_type=target_client)
        
        results = extract_contents(data, renderer_type="video")
        
        response = {
            "success": True,
            "region": region,
            "count": len(results),
            "results": results,
            "raw_data": data
        }
        
        cache_service.set("trending", "trending", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trending: {str(e)}")


@router.get("/homepage")
async def get_homepage(
    client: Optional[str] = Query(None, description="Client type")
):
    """
    Get YouTube homepage feed
    
    **Example**: `/api/homepage`
    """
    try:
        params = {"client": client}
        cached = cache_service.get("default", "homepage", params)
        if cached:
            return cached
        
        data = client_manager.browse("FEwhat_to_watch", client_type=client)
        
        results = extract_contents(data, renderer_type="video")
        
        response = {
            "success": True,
            "count": len(results),
            "results": results,
            "raw_data": data
        }
        
        cache_service.set("default", "homepage", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get homepage: {str(e)}")
