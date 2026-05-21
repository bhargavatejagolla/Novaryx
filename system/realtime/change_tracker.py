"""
NOVARYX - Change Tracker
Tracks every change during generation for diff viewing and rollback.

Tracks:
  - Files created/modified/deleted
  - Content changes between versions
  - Generation phase at time of change
  - Agent responsible for each change
"""

import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger("novaryx.change_tracker")


@dataclass
class FileChange:
    """A single file change record"""
    filepath: str
    change_type: str  # created, modified, deleted
    content_hash: str
    size_bytes: int
    phase: str = ""
    agent: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    previous_hash: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "file": self.filepath,
            "change": self.change_type,
            "size": self.size_bytes,
            "phase": self.phase,
            "agent": self.agent,
            "timestamp": self.timestamp,
        }


@dataclass
class GenerationSnapshot:
    """A complete snapshot at a point in time"""
    snapshot_id: str
    timestamp: str
    phase: str
    files: Dict[str, str]  # filepath → content_hash
    total_files: int
    total_size_bytes: int
    
    def to_dict(self) -> Dict:
        return {
            "id": self.snapshot_id,
            "timestamp": self.timestamp,
            "phase": self.phase,
            "files": self.total_files,
            "size": self.total_size_bytes,
        }


class ChangeTracker:
    """
    Tracks all changes during a generation session.
    
    Enables:
    - Diff viewing between versions
    - Rollback to any snapshot
    - Change history browsing
    - Agent accountability
    """
    
    def __init__(self):
        self.changes: List[FileChange] = []
        self.snapshots: List[GenerationSnapshot] = []
        self.current_files: Dict[str, str] = {}  # filepath → content_hash
        self.generation_id: Optional[str] = None
        self.total_changes = 0
        self.total_bytes = 0
    
    def start_tracking(self, generation_id: str):
        """Start tracking a new generation"""
        self.generation_id = generation_id
        self.changes = []
        self.snapshots = []
        self.current_files = {}
        self.total_changes = 0
        self.total_bytes = 0
        logger.info(f"Change tracking started: {generation_id}")
    
    def record_file_created(self, filepath: str, content: str, phase: str = "", agent: str = ""):
        """Record a file creation"""
        content_hash = self._hash_content(content)
        size = len(content)
        
        change = FileChange(
            filepath=filepath,
            change_type="created",
            content_hash=content_hash,
            size_bytes=size,
            phase=phase,
            agent=agent,
        )
        
        self.changes.append(change)
        self.current_files[filepath] = content_hash
        self.total_changes += 1
        self.total_bytes += size
    
    def record_file_modified(self, filepath: str, new_content: str, phase: str = "", agent: str = ""):
        """Record a file modification"""
        new_hash = self._hash_content(new_content)
        old_hash = self.current_files.get(filepath)
        
        change = FileChange(
            filepath=filepath,
            change_type="modified",
            content_hash=new_hash,
            size_bytes=len(new_content),
            phase=phase,
            agent=agent,
            previous_hash=old_hash,
        )
        
        self.changes.append(change)
        self.current_files[filepath] = new_hash
        self.total_changes += 1
    
    def record_file_deleted(self, filepath: str, phase: str = "", agent: str = ""):
        """Record a file deletion"""
        old_hash = self.current_files.get(filepath, "")
        
        change = FileChange(
            filepath=filepath,
            change_type="deleted",
            content_hash="",
            size_bytes=0,
            phase=phase,
            agent=agent,
            previous_hash=old_hash,
        )
        
        self.changes.append(change)
        if filepath in self.current_files:
            del self.current_files[filepath]
        self.total_changes += 1
    
    def create_snapshot(self, phase: str) -> str:
        """Create a snapshot of current state"""
        snapshot_id = f"snap_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        total_size = sum(
            len(h) for h in self.current_files.values()
        )
        
        snapshot = GenerationSnapshot(
            snapshot_id=snapshot_id,
            timestamp=datetime.now().isoformat(),
            phase=phase,
            files=dict(self.current_files),
            total_files=len(self.current_files),
            total_size_bytes=total_size,
        )
        
        self.snapshots.append(snapshot)
        logger.info(f"Snapshot created: {snapshot_id} ({snapshot.total_files} files)")
        
        return snapshot_id
    
    def _hash_content(self, content: str) -> str:
        """Hash content for comparison"""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def get_changes_by_phase(self) -> Dict[str, List[Dict]]:
        """Get changes grouped by phase"""
        by_phase = {}
        for change in self.changes:
            phase = change.phase or "unknown"
            if phase not in by_phase:
                by_phase[phase] = []
            by_phase[phase].append(change.to_dict())
        return by_phase
    
    def get_changes_by_agent(self) -> Dict[str, List[Dict]]:
        """Get changes grouped by agent"""
        by_agent = {}
        for change in self.changes:
            agent = change.agent or "system"
            if agent not in by_agent:
                by_agent[agent] = []
            by_agent[agent].append(change.to_dict())
        return by_agent
    
    def get_recent_changes(self, count: int = 20) -> List[Dict]:
        """Get most recent changes"""
        return [c.to_dict() for c in self.changes[-count:]]
    
    def get_change_summary(self) -> Dict[str, Any]:
        """Get change summary statistics"""
        created = sum(1 for c in self.changes if c.change_type == "created")
        modified = sum(1 for c in self.changes if c.change_type == "modified")
        deleted = sum(1 for c in self.changes if c.change_type == "deleted")
        
        return {
            "generation_id": self.generation_id,
            "total_changes": self.total_changes,
            "files_created": created,
            "files_modified": modified,
            "files_deleted": deleted,
            "current_files": len(self.current_files),
            "snapshots": len(self.snapshots),
            "total_bytes": self.total_bytes,
            "by_phase": {
                phase: len(changes)
                for phase, changes in self.get_changes_by_phase().items()
            },
            "recent": self.get_recent_changes(5),
        }
    
    def display_summary(self):
        """Display change tracking summary"""
        summary = self.get_change_summary()
        
        print("\n" + "=" * 50)
        print("📝 CHANGE TRACKER SUMMARY")
        print("=" * 50)
        print(f"   Generation: {summary['generation_id']}")
        print(f"   Total Changes: {summary['total_changes']}")
        print(f"   Created: {summary['files_created']}")
        print(f"   Modified: {summary['files_modified']}")
        print(f"   Current Files: {summary['current_files']}")
        print(f"   Snapshots: {summary['snapshots']}")
        print(f"   Total Size: {summary['total_bytes']:,} bytes")
        
        if summary.get("by_phase"):
            print(f"\n   Changes by Phase:")
            for phase, count in summary["by_phase"].items():
                print(f"      {phase}: {count}")
        
        print("=" * 50)
    
    def stop_tracking(self):
        """Stop tracking"""
        self.create_snapshot("final")
        logger.info(f"Change tracking stopped: {self.generation_id}")
        self.display_summary()


# ---- Test ----

def test_realtime_system():
    """Test real-time system"""
    
    from .websocket_server import WebSocketServer
    from .live_preview import LivePreviewManager
    
    print("\n" + "=" * 60)
    print("🧪 REAL-TIME SYSTEM TEST")
    print("=" * 60)
    
    # WebSocket server
    ws = WebSocketServer()
    ws.start()
    client = ws.add_client()
    ws.subscribe(client.client_id, "*")
    
    # Live preview
    preview = LivePreviewManager(ws)
    preview.start_generation("test-gen-001", "TestProject", 5)
    
    # Simulate generation
    preview.on_phase_start("Design System", 1, 5)
    preview.on_file_generated("src/styles/tokens.css", ":root { --primary: #7c3aed; }")
    preview.on_file_generated("src/App.tsx", "export default function App() {}")
    preview.on_component_selected("StatsCard", "stats")
    preview.on_phase_complete("Design System")
    
    preview.on_phase_start("Component Generation", 2, 5)
    preview.on_agent_status("frontend", "busy", "generating page")
    preview.on_file_generated("src/components/StatsCard.tsx", "export function StatsCard() {}")
    preview.on_agent_status("frontend", "idle")
    preview.on_phase_complete("Component Generation")
    
    preview.complete_generation("TestProject")
    
    # Change tracker
    tracker = ChangeTracker()
    tracker.start_tracking("test-gen-001")
    tracker.record_file_created("src/App.tsx", "content", "design", "architect")
    tracker.record_file_created("src/main.tsx", "content", "design", "architect")
    tracker.record_file_modified("src/App.tsx", "updated content", "repair", "repair")
    tracker.create_snapshot("after_design")
    tracker.stop_tracking()
    
    # Results
    print(f"\n   WebSocket clients: {ws.get_stats()['clients_connected']}")
    print(f"   Queued messages: {ws.get_stats()['queued_messages']}")
    print(f"   Preview files: {len(preview.files_generated)}")
    print(f"   Tracked changes: {tracker.total_changes}")
    
    ws.stop()
    preview.cleanup_preview()
    
    print("\n✅ Real-Time System test complete")
    
    return ws, preview, tracker


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_realtime_system()