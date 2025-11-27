"""
Response Parser Utilities
Extracts and cleans data from InnerTube responses
"""
from typing import Dict, Any, List, Optional
import re


def get_text(obj: Any) -> str:
    """Extract text from various InnerTube text objects"""
    if isinstance(obj, str):
        return obj
    
    if isinstance(obj, dict):
        if "simpleText" in obj:
            return obj["simpleText"]
        elif "runs" in obj:
            return "".join(run.get("text", "") for run in obj["runs"])
    
    return ""


def parse_duration(duration_text: str) -> int:
    """Parse duration text (e.g., '3:45') to seconds"""
    try:
        parts = duration_text.split(":")
        if len(parts) == 2:  # MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except:
        pass
    return 0


def parse_number(text: str) -> int:
    """Parse number from text (e.g., '1.2M views' -> 1200000)"""
    if not text:
        return 0
    
    text = text.upper().replace(",", "")
    
    # Extract number
    match = re.search(r'([\d.]+)\s*([KMB])?', text)
    if not match:
        return 0
    
    num = float(match.group(1))
    multiplier = match.group(2)
    
    if multiplier == 'K':
        return int(num * 1000)
    elif multiplier == 'M':
        return int(num * 1000000)
    elif multiplier == 'B':
        return int(num * 1000000000)
    
    return int(num)


def get_thumbnail(thumbnails: List[Dict[str, Any]], quality: str = "high") -> Optional[str]:
    """Get thumbnail URL from thumbnails list"""
    if not thumbnails:
        return None
    
    if quality == "high" and len(thumbnails) > 0:
        return thumbnails[-1].get("url")
    elif quality == "medium" and len(thumbnails) > 1:
        return thumbnails[len(thumbnails) // 2].get("url")
    elif quality == "low" and len(thumbnails) > 0:
        return thumbnails[0].get("url")
    
    return thumbnails[0].get("url") if thumbnails else None


def parse_video_renderer(renderer: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a video renderer object"""
    video_id = renderer.get("videoId", "")
    
    title = get_text(renderer.get("title", {}))
    
    thumbnails = renderer.get("thumbnail", {}).get("thumbnails", [])
    thumbnail = get_thumbnail(thumbnails)
    
    duration_text = get_text(renderer.get("lengthText", {}))
    duration_seconds = parse_duration(duration_text)
    
    view_count_text = get_text(renderer.get("viewCountText", {}))
    view_count = parse_number(view_count_text)
    
    published_time = get_text(renderer.get("publishedTimeText", {}))
    
    channel_name = get_text(renderer.get("ownerText", {}))
    channel_id = ""
    if "ownerText" in renderer and "runs" in renderer["ownerText"]:
        runs = renderer["ownerText"]["runs"]
        if runs and "navigationEndpoint" in runs[0]:
            browse_endpoint = runs[0]["navigationEndpoint"].get("browseEndpoint", {})
            channel_id = browse_endpoint.get("browseId", "")
    
    description = get_text(renderer.get("descriptionSnippet", {}))
    
    return {
        "video_id": video_id,
        "title": title,
        "thumbnail": thumbnail,
        "duration": duration_text,
        "duration_seconds": duration_seconds,
        "views": view_count,
        "view_count_text": view_count_text,
        "published": published_time,
        "channel": {
            "name": channel_name,
            "id": channel_id
        },
        "description": description
    }


def parse_channel_renderer(renderer: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a channel renderer object"""
    channel_id = renderer.get("channelId", "")
    title = get_text(renderer.get("title", {}))
    
    thumbnails = renderer.get("thumbnail", {}).get("thumbnails", [])
    thumbnail = get_thumbnail(thumbnails)
    
    subscriber_count = get_text(renderer.get("subscriberCountText", {}))
    video_count = get_text(renderer.get("videoCountText", {}))
    
    description = get_text(renderer.get("descriptionSnippet", {}))
    
    return {
        "channel_id": channel_id,
        "title": title,
        "thumbnail": thumbnail,
        "subscribers": subscriber_count,
        "video_count": video_count,
        "description": description
    }


def parse_playlist_renderer(renderer: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a playlist renderer object"""
    playlist_id = renderer.get("playlistId", "")
    title = get_text(renderer.get("title", {}))
    
    thumbnails = renderer.get("thumbnails", [])
    if thumbnails and isinstance(thumbnails[0], dict):
        thumbnails = thumbnails[0].get("thumbnails", [])
    thumbnail = get_thumbnail(thumbnails)
    
    video_count = get_text(renderer.get("videoCount", {}))
    
    channel_name = get_text(renderer.get("shortBylineText", {}))
    
    return {
        "playlist_id": playlist_id,
        "title": title,
        "thumbnail": thumbnail,
        "video_count": video_count,
        "channel": channel_name
    }


def extract_contents(data: Dict[str, Any], renderer_type: str = "video") -> List[Dict[str, Any]]:
    """Extract and parse contents from InnerTube response"""
    results = []
    
    # Navigate through common response structures
    contents = data
    for key in ["contents", "onResponseReceivedCommands", "continuationContents"]:
        if key in contents:
            contents = contents[key]
            break
            
    # Handle twoColumnSearchResultsRenderer (Search results)
    if isinstance(contents, dict) and "twoColumnSearchResultsRenderer" in contents:
        contents = contents["twoColumnSearchResultsRenderer"].get("primaryContents", {})
        if "sectionListRenderer" in contents:
            contents = contents["sectionListRenderer"].get("contents", [])
            
    # Handle singleColumnBrowseResultsRenderer (Channel/Browse results)
    elif isinstance(contents, dict) and "singleColumnBrowseResultsRenderer" in contents:
        tabs = contents["singleColumnBrowseResultsRenderer"].get("tabs", [])
        if tabs:
            # Usually the first tab or the selected one
            for tab in tabs:
                if "tabRenderer" in tab and tab["tabRenderer"].get("selected", False):
                    content = tab["tabRenderer"].get("content", {})
                    if "sectionListRenderer" in content:
                        contents = content["sectionListRenderer"].get("contents", [])
                    elif "richGridRenderer" in content:
                        contents = content["richGridRenderer"].get("contents", [])
                    break
            # Fallback to first tab content if no selected tab found
            if isinstance(contents, dict) and "singleColumnBrowseResultsRenderer" in data.get("contents", {}):
                 if tabs and "tabRenderer" in tabs[0]:
                    content = tabs[0]["tabRenderer"].get("content", {})
                    if "sectionListRenderer" in content:
                        contents = content["sectionListRenderer"].get("contents", [])
                    elif "richGridRenderer" in content:
                        contents = content["richGridRenderer"].get("contents", [])

    # Find the main content container
    if isinstance(contents, list):
        for item in contents:
            if "itemSectionRenderer" in item:
                contents = item["itemSectionRenderer"].get("contents", [])
                break
            elif "appendContinuationItemsAction" in item:
                contents = item["appendContinuationItemsAction"].get("continuationItems", [])
                break
    
    # Parse individual items
    if isinstance(contents, list):
        for item in contents:
            try:
                if "videoRenderer" in item and renderer_type == "video":
                    results.append(parse_video_renderer(item["videoRenderer"]))
                elif "channelRenderer" in item and renderer_type == "channel":
                    results.append(parse_channel_renderer(item["channelRenderer"]))
                elif "playlistRenderer" in item and renderer_type == "playlist":
                    results.append(parse_playlist_renderer(item["playlistRenderer"]))
                elif "videoRenderer" in item:  # Default to video
                    results.append(parse_video_renderer(item["videoRenderer"]))
            except Exception as e:
                # Skip items that fail to parse
                continue
    
    return results
