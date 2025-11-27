"""
Playlist API Routes
Endpoints for playlist information and videos
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from services import client_manager, cache_service
from utils import extract_contents

router = APIRouter(prefix="/api/playlist", tags=["Playlists"])


@router.get("/{playlist_id}")
async def get_playlist(
    playlist_id: str,
    client: Optional[str] = Query(None, description="Client type")
):
    """
    Get playlist details
    
    **Example**: `/api/playlist/PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf`
    """
    try:
        params = {"playlist_id": playlist_id, "client": client}
        cached = cache_service.get("playlist", "playlist_info", params)
        if cached:
            return cached
        
        data = client_manager.browse(f"VL{playlist_id}", client_type=client)
        
        response = {
            "success": True,
            "playlist_id": playlist_id,
            "data": data
        }
        
        cache_service.set("playlist", "playlist_info", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get playlist: {str(e)}")


@router.get("/{playlist_id}/videos")
async def get_playlist_videos(
    playlist_id: str,
    client: Optional[str] = Query(None, description="Client type"),
    limit: Optional[int] = Query(50, description="Maximum number of videos")
):
    """
    Get all videos in a playlist
    
    **Example**: `/api/playlist/PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf/videos`
    """
    try:
        params = {"playlist_id": playlist_id, "client": client, "limit": limit}
        cached = cache_service.get("playlist", "playlist_videos", params)
        if cached:
            return cached
        
        data = client_manager.browse(f"VL{playlist_id}", client_type=client)
        
        results = extract_contents(data, renderer_type="video")
        
        if limit:
            results = results[:limit]
        
        response = {
            "success": True,
            "playlist_id": playlist_id,
            "count": len(results),
            "videos": results,
            "raw_data": data
        }
        
        cache_service.set("playlist", "playlist_videos", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get playlist videos: {str(e)}")
