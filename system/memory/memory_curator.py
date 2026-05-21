"""
NOVARYX - Memory Quality Curator
Ensures only high-quality, stable code enters long-term memory.
"""

import logging
import json
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger("novaryx.memory_curator")

class MemoryCurator:
    """
    Filters and curates project modules before they are indexed in RAG.
    
    Policies:
    - TrustScore > 0.95 -> Golden Example (High Weight)
    - TrustScore > 0.80 -> Standard Example
    - TrustScore < 0.80 -> Cautionary Example (Ignore for RAG generation)
    - RepairCount > 2   -> Log as "Volatile"
    """
    
    def __init__(self, trust_threshold: float = 0.95):
        self.trust_threshold = trust_threshold
        
    def filter_files(self, files: Dict[str, str], trust_scores: Dict[str, float]) -> Dict[str, str]:
        """
        Filter out files that don't meet the trust threshold for golden indexing.
        """
        golden_files = {}
        for path, score in trust_scores.items():
            if score >= self.trust_threshold and path in files:
                golden_files[path] = files[path]
                
        logger.info(f"Curated {len(golden_files)}/{len(files)} files for Golden Memory")
        return golden_files

    def get_curation_metadata(self, project_name: str, trust_scores: Dict[str, float]) -> Dict:
        """
        Produce a quality report for the memory entry.
        """
        avg_trust = sum(trust_scores.values()) / max(len(trust_scores), 1)
        volatile_files = [p for p, s in trust_scores.items() if s < 0.8]
        
        return {
            "avg_trust": avg_trust,
            "is_high_quality": avg_trust >= self.trust_threshold,
            "volatile_count": len(volatile_files),
            "volatile_files": volatile_files[:5],
            "curated_at": __import__('datetime').datetime.now().isoformat()
        }
