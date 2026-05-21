"""
NOVARYX - WebSocket Server
Real-time communication between generation engine and preview.

Enables:
  - Streaming generation progress to browser
  - Live file updates during generation
  - Agent status broadcasting
  - Error notifications
"""

import json
import time
import logging
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import uuid

logger = logging.getLogger("novaryx.websocket")


@dataclass
class WebSocketClient:
    """Connected client"""
    client_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    connected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    subscriptions: List[str] = field(default_factory=list)
    last_activity: float = field(default_factory=time.time)


class WebSocketServer:
    """
    WebSocket server for real-time communication.
    
    Manages:
    - Client connections
    - Event broadcasting
    - Room/subscription management
    - Heartbeat monitoring
    """
    
    def __init__(self, host: str = "localhost", port: int = 9001):
        self.host = host
        self.port = port
        self.clients: Dict[str, WebSocketClient] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.rooms: Dict[str, List[str]] = {}
        self.running = False
        
        # Message queue for async processing
        self.message_queue: List[Dict] = []
        self._lock = threading.Lock()
        
        logger.info(f"WebSocket server configured: {host}:{port}")
    
    def add_client(self, client_id: str = None) -> WebSocketClient:
        """Register a new client"""
        client = WebSocketClient(client_id=client_id)
        with self._lock:
            self.clients[client.client_id] = client
        logger.info(f"Client connected: {client.client_id}")
        return client
    
    def remove_client(self, client_id: str):
        """Remove a client"""
        with self._lock:
            if client_id in self.clients:
                del self.clients[client_id]
        logger.info(f"Client disconnected: {client_id}")
    
    def subscribe(self, client_id: str, event_type: str):
        """Subscribe a client to an event type"""
        with self._lock:
            if client_id in self.clients:
                if event_type not in self.clients[client_id].subscriptions:
                    self.clients[client_id].subscriptions.append(event_type)
    
    def broadcast(self, event_type: str, data: Dict[str, Any]):
        """
        Broadcast an event to all subscribed clients.
        
        Event types:
        - generation.progress - Pipeline progress updates
        - generation.phase - Phase started/completed
        - generation.file - File generated
        - generation.component - Component generated
        - generation.error - Error occurred
        - generation.complete - Generation finished
        - agent.status - Agent status changed
        """
        message = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }
        
        with self._lock:
            self.message_queue.append(message)
    
    def broadcast_phase_start(self, phase_name: str, phase_num: int, total: int):
        """Broadcast phase start"""
        self.broadcast("generation.phase", {
            "type": "start",
            "phase": phase_name,
            "phase_num": phase_num,
            "total_phases": total,
            "progress": f"{(phase_num / total) * 100:.0f}%"
        })
    
    def broadcast_phase_complete(self, phase_name: str, result: Dict = None):
        """Broadcast phase completion"""
        self.broadcast("generation.phase", {
            "type": "complete",
            "phase": phase_name,
            "result": result or {}
        })
    
    def broadcast_file_generated(self, filepath: str, size: int):
        """Broadcast file generation"""
        self.broadcast("generation.file", {
            "filepath": filepath,
            "size_bytes": size,
            "type": filepath.split(".")[-1] if "." in filepath else "unknown"
        })
    
    def broadcast_component(self, component_name: str, slot: str):
        """Broadcast component selection"""
        self.broadcast("generation.component", {
            "component": component_name,
            "slot": slot,
        })
    
    def broadcast_error(self, error: str, phase: str = ""):
        """Broadcast error"""
        self.broadcast("generation.error", {
            "error": error,
            "phase": phase,
        })
    
    def broadcast_complete(self, project_name: str, files_count: int):
        """Broadcast generation complete"""
        self.broadcast("generation.complete", {
            "project": project_name,
            "files": files_count,
            "message": f"✅ {project_name} generated with {files_count} files"
        })
    
    def broadcast_agent_status(self, agent_id: str, status: str, task: str = ""):
        """Broadcast agent status"""
        self.broadcast("agent.status", {
            "agent": agent_id,
            "status": status,
            "task": task,
        })
    
    def get_events_for_client(self, client_id: str) -> List[Dict]:
        """Get pending events for a client"""
        with self._lock:
            if client_id not in self.clients:
                return []
            
            client = self.clients[client_id]
            events = []
            
            for msg in self.message_queue:
                if msg["event"] in client.subscriptions or "*" in client.subscriptions:
                    events.append(msg)
            
            client.last_activity = time.time()
            return events
    
    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        return {
            "clients_connected": len(self.clients),
            "queued_messages": len(self.message_queue),
            "uptime": "active",
            "subscriptions": {
                cid: client.subscriptions
                for cid, client in self.clients.items()
            }
        }
    
    def start(self):
        """Start the WebSocket server"""
        self.running = True
        logger.info(f"WebSocket server started on {self.host}:{self.port}")
    
    def stop(self):
        """Stop the WebSocket server"""
        self.running = False
        self.clients.clear()
        self.message_queue.clear()
        logger.info("WebSocket server stopped")