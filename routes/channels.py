"""
Channel API Routes
Endpoints for channel information and content
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from services import client_manager, cache_service
from utils import extract_contents

router = APIRouter(prefix="/api/channel", tags=["Channels"])


@router.get("/{channel_id}")
async def get_channel(
    channel_id: str,
    client: Optional[str] = Query(None, description="Client type")
):
    """
    Get channel information
    
    **Example**: `/api/channel/UCX6OQ3DkcsbYNE6H8uQQuVA`
    """
    try:
        params = {"channel_id": channel_id, "client": client}
        cached = cache_service.get("channel", "channel_info", params)
        if cached:
            return cached
        
        data = client_manager.browse(channel_id, client_type=client)
        
        response = {
            "success": True,
            "channel_id": channel_id,
            "data": data
        }
        
        cache_service.set("channel", "channel_info", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get channel: {str(e)}")


@router.get("/{channel_id}/videos")
async def get_channel_videos(
    channel_id: str,
    client: Optional[str] = Query(None, description="Client type"),
    limit: Optional[int] = Query(20, description="Maximum number of videos")
):
    """
    Get channel videos
    
    **Example**: `/api/channel/UCX6OQ3DkcsbYNE6H8uQQuVA/videos`
    """
    try:
        params = {"channel_id": channel_id, "client": client, "limit": limit}
        cached = cache_service.get("channel", "channel_videos", params)
        if cached:
            return cached
        
        # Browse channel videos tab
        data = client_manager.browse(f"{channel_id}/videos", client_type=client)
        
        results = extract_contents(data, renderer_type="video")
        
        if limit:
            results = results[:limit]
        
        response = {
            "success": True,
            "channel_id": channel_id,
            "count": len(results),
            "videos": results,
            "raw_data": data
        }
        
        cache_service.set("channel", "channel_videos", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get channel videos: {str(e)}")


@router.get("/{channel_id}/playlists")
async def get_channel_playlists(
    channel_id: str,
    client: Optional[str] = Query(None, description="Client type")
):
    """
    Get channel playlists
    
    **Example**: `/api/channel/UCX6OQ3DkcsbYNE6H8uQQuVA/playlists`
    """
    try:
        params = {"channel_id": channel_id, "client": client}
        cached = cache_service.get("channel", "channel_playlists", params)
        if cached:
            return cached
        
        data = client_manager.browse(f"{channel_id}/playlists", client_type=client)
        
        results = extract_contents(data, renderer_type="playlist")
        
        response = {
            "success": True,
            "channel_id": channel_id,
            "count": len(results),
            "playlists": results,
            "raw_data": data
        }
        
        cache_service.set("channel", "channel_playlists", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get channel playlists: {str(e)}")


@router.get("/{channel_id}/about")
async def get_channel_about(
    channel_id: str,
    client: Optional[str] = Query(None, description="Client type")
):
    """
    Get channel about information
    
    **Example**: `/api/channel/UCX6OQ3DkcsbYNE6H8uQQuVA/about`
    """
    try:
        params = {"channel_id": channel_id, "client": client}
        cached = cache_service.get("channel", "channel_about", params)
        if cached:
            return cached
        
        data = client_manager.browse(f"{channel_id}/about", client_type=client)
        
        response = {
            "success": True,
            "channel_id": channel_id,
            "data": data
        }
        
        cache_service.set("channel", "channel_about", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get channel about: {str(e)}")


@router.get("/{channel_id}/community")
async def get_channel_community(
    channel_id: str,
    client: Optional[str] = Query(None, description="Client type")
):
    """
    Get channel community posts
    
    **Example**: `/api/channel/UCX6OQ3DkcsbYNE6H8uQQuVA/community`
    """
    try:
        params = {"channel_id": channel_id, "client": client}
        cached = cache_service.get("channel", "channel_community", params)
        if cached:
            return cached
        
        data = client_manager.browse(f"{channel_id}/community", client_type=client)
        
        response = {
            "success": True,
            "channel_id": channel_id,
            "data": data
        }
        
        cache_service.set("channel", "channel_community", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get community posts: {str(e)}")
