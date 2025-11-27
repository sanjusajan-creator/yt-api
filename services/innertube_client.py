"""
InnerTube Client Service
Manages multiple InnerTube clients with automatic rotation and error handling
"""
import innertube
from typing import Dict, Any, Optional, List
import logging
from config import (
    INNERTUBE_CLIENTS, 
    INNERTUBE_MUSIC_CLIENTS,
    DEFAULT_CLIENT,
    DEFAULT_MUSIC_CLIENT,
    MAX_RETRIES
)

logger = logging.getLogger(__name__)


class InnerTubeClientManager:
    """Manages InnerTube clients with automatic rotation and error handling"""
    
    def __init__(self):
        self.clients: Dict[str, innertube.InnerTube] = {}
        self.music_clients: Dict[str, innertube.InnerTube] = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize all YouTube clients"""
        for client_type in INNERTUBE_CLIENTS:
            try:
                self.clients[client_type] = innertube.InnerTube(client_type)
                logger.info(f"Initialized {client_type} client")
            except Exception as e:
                logger.error(f"Failed to initialize {client_type} client: {e}")
        
        for client_type in INNERTUBE_MUSIC_CLIENTS:
            try:
                self.music_clients[client_type] = innertube.InnerTube(client_type)
                logger.info(f"Initialized {client_type} music client")
            except Exception as e:
                logger.error(f"Failed to initialize {client_type} music client: {e}")
    
    def get_client(self, client_type: Optional[str] = None) -> innertube.InnerTube:
        """Get a YouTube client by type"""
        if client_type and client_type in self.clients:
            return self.clients[client_type]
        return self.clients.get(DEFAULT_CLIENT, next(iter(self.clients.values())))
    
    def get_music_client(self, client_type: Optional[str] = None) -> innertube.InnerTube:
        """Get a YouTube Music client by type"""
        if client_type and client_type in self.music_clients:
            return self.music_clients[client_type]
        return self.music_clients.get(DEFAULT_MUSIC_CLIENT, next(iter(self.music_clients.values())))
    
    def execute_with_retry(
        self, 
        method_name: str, 
        client_type: Optional[str] = None,
        is_music: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute an InnerTube method with automatic retry on failure
        
        Args:
            method_name: Name of the method to call (e.g., 'search', 'player', 'browse')
            client_type: Optional client type to use
            is_music: Whether to use music client
            **kwargs: Arguments to pass to the method
        
        Returns:
            Response data from InnerTube
        """
        client = self.get_music_client(client_type) if is_music else self.get_client(client_type)
        
        for attempt in range(MAX_RETRIES):
            try:
                # Check if method exists
                if not hasattr(client, method_name):
                    # Use generic call method
                    return client(method_name, **kwargs)
                
                # Call the specific method
                method = getattr(client, method_name)
                result = method(**kwargs)
                return result
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {method_name}: {e}")
                
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"All retries exhausted for {method_name}")
                    raise
                
                # Try with a different client on retry
                if not is_music and len(self.clients) > 1:
                    available_clients = [c for c in self.clients.keys() if c != client_type]
                    if available_clients:
                        client_type = available_clients[0]
                        client = self.get_client(client_type)
        
        raise Exception(f"Failed to execute {method_name}")
    
    def search(self, query: str, client_type: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Search YouTube"""
        return self.execute_with_retry("search", client_type, query=query, **kwargs)
    
    def player(self, video_id: str, client_type: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Get video player data"""
        return self.execute_with_retry("player", client_type, video_id=video_id, **kwargs)
    
    def browse(self, browse_id: str, client_type: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Browse YouTube pages"""
        return self.execute_with_retry("browse", client_type, browse_id=browse_id, **kwargs)
    
    def next(self, video_id: str, client_type: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Get next/related videos"""
        return self.execute_with_retry("next", client_type, video_id=video_id, **kwargs)
    
    def music_search(self, query: str, client_type: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Search YouTube Music"""
        return self.execute_with_retry("search", client_type, is_music=True, query=query, **kwargs)


# Global client manager instance
client_manager = InnerTubeClientManager()
