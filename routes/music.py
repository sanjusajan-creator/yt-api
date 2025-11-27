"""
YouTube Music API Routes
Endpoints for YouTube Music
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from services import client_manager, cache_service
from utils import extract_contents

router = APIRouter(prefix="/api/music", tags=["YouTube Music"])


@router.get("/search")
async def music_search(
    query: str = Query(..., description="Search query"),
    client: Optional[str] = Query(None, description="Music client type"),
    limit: Optional[int] = Query(20, description="Maximum number of results")
):
    """
    Search YouTube Music
    
    **Example**: `/api/music/search?query=imagine+dragons`
    """
    try:
        params = {"query": query, "client": client, "limit": limit}
        cached = cache_service.get("music", "music_search", params)
        if cached:
            return cached
        
        data = client_manager.music_search(query, client_type=client)
        
        results = extract_contents(data)
        
        if limit:
            results = results[:limit]
        
        response = {
            "success": True,
            "query": query,
            "count": len(results),
            "results": results,
            "raw_data": data
        }
        
        cache_service.set("music", "music_search", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Music search failed: {str(e)}")


@router.get("/home")
async def music_home(
    client: Optional[str] = Query(None, description="Music client type")
):
    """
    Get YouTube Music home feed
    
    **Example**: `/api/music/home`
    """
    try:
        params = {"client": client}
        cached = cache_service.get("music", "music_home", params)
        if cached:
            return cached
        
        data = client_manager.execute_with_retry(
            "browse",
            client_type=client,
            is_music=True,
            browse_id="FEmusic_home"
        )
        
        response = {
            "success": True,
            "data": data
        }
        
        cache_service.set("music", "music_home", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get music home: {str(e)}")


@router.get("/artist/{artist_id}")
async def get_artist(
    artist_id: str,
    client: Optional[str] = Query(None, description="Music client type")
):
    """
    Get artist information
    
    **Example**: `/api/music/artist/UCmMUZbaYdNH0bEd1PAlAqsA`
    """
    try:
        params = {"artist_id": artist_id, "client": client}
        cached = cache_service.get("music", "artist", params)
        if cached:
            return cached
        
        data = client_manager.execute_with_retry(
            "browse",
            client_type=client,
            is_music=True,
            browse_id=artist_id
        )
        
        response = {
            "success": True,
            "artist_id": artist_id,
            "data": data
        }
        
        cache_service.set("music", "artist", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get artist: {str(e)}")


@router.get("/album/{album_id}")
async def get_album(
    album_id: str,
    client: Optional[str] = Query(None, description="Music client type")
):
    """
    Get album details
    
    **Example**: `/api/music/album/MPREb_BQZvl3BFGay`
    """
    try:
        params = {"album_id": album_id, "client": client}
        cached = cache_service.get("music", "album", params)
        if cached:
            return cached
        
        data = client_manager.execute_with_retry(
            "browse",
            client_type=client,
            is_music=True,
            browse_id=album_id
        )
        
        response = {
            "success": True,
            "album_id": album_id,
            "data": data
        }
        
        cache_service.set("music", "album", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get album: {str(e)}")


@router.get("/playlist/{playlist_id}")
async def get_music_playlist(
    playlist_id: str,
    client: Optional[str] = Query(None, description="Music client type")
):
    """
    Get music playlist
    
    **Example**: `/api/music/playlist/RDCLAK5uy_kmPRjHDECIcuVwnKsx`
    """
    try:
        params = {"playlist_id": playlist_id, "client": client}
        cached = cache_service.get("music", "music_playlist", params)
        if cached:
            return cached
        
        data = client_manager.execute_with_retry(
            "browse",
            client_type=client,
            is_music=True,
            browse_id=f"VL{playlist_id}"
        )
        
        response = {
            "success": True,
            "playlist_id": playlist_id,
            "data": data
        }
        
        cache_service.set("music", "music_playlist", params, response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get music playlist: {str(e)}")
