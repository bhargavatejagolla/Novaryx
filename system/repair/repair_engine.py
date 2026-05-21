"""
NOVARYX - Repair Engine
Main orchestrator for the repair pipeline.

Flow:
  Files → Bug Detection → Pattern Fixes → LLM Fixes → Validation → Report
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from .bug_detector import BugDetector, Bug, BugType
from .fixers import FixRegistry, get_fixer
from .llm_repairer import LLMRepairer
from .repair_validator import RepairValidator
from system.rag_engine.chromadb_client import ChromaDBClient

logger = logging.getLogger("novaryx.repair_engine")


@dataclass
class RepairResult:
    """Result of a repair operation"""
    success: bool
    files_repaired: int
    bugs_found: int
    bugs_fixed: int
    bugs_remaining: int
    repair_rounds: int
    repaired_files: Dict[str, str] = field(default_factory=dict)
    unfixable_bugs: List[Bug] = field(default_factory=list)
    report: Dict[str, Any] = field(default_factory=dict)


class RepairEngine:
    """
    Complete repair pipeline.
    
    Orchestrates: Detect → Pattern Fix → LLM Fix → Validate
    Retries up to max_rounds times.
    """
    
    def __init__(self, use_llm: bool = True, max_rounds: int = 3):
        self.use_llm = use_llm
        self.max_rounds = max_rounds
        self.detector = BugDetector()
        self.llm_repairer = LLMRepairer() if use_llm else None
        self.validator = RepairValidator()
        self.chroma_client = None
        try:
            self.chroma_client = ChromaDBClient()
        except BaseException as e:
            logger.warning(f"Could not initialize ChromaDB in RepairEngine: {e}")
    
    def repair_project(self, files: Dict[str, str]) -> RepairResult:
        """
        Repair all files in a project.
        
        Args:
            files: {filepath: content}
        
        Returns:
            RepairResult with repaired files and stats
        """
        
        print("\n" + "=" * 60)
        print("🔧 REPAIR ENGINE")
        print("=" * 60)
        
        repaired_files = dict(files)
        all_bugs_fixed = 0
        total_rounds = 0
        unfixable = []
        
        for round_num in range(1, self.max_rounds + 1):
            total_rounds = round_num
            
            # Step 1: Detect bugs
            bugs = self.detector.scan_project(repaired_files)
            
            if not bugs:
                print(f"   Round {round_num}: No bugs found!")
                break
            
            summary = self.detector.get_bug_summary(bugs)
            print(f"\n   Round {round_num}: {summary['total']} bugs found")
            print(f"      Critical: {summary['by_severity']['critical']}")
            print(f"      Errors: {summary['by_severity']['error']}")
            print(f"      Warnings: {summary['by_severity']['warning']}")
            
            # Step 2: Group bugs by file
            bugs_by_file: Dict[str, List[Bug]] = {}
            for bug in bugs:
                if bug.file_path not in bugs_by_file:
                    bugs_by_file[bug.file_path] = []
                bugs_by_file[bug.file_path].append(bug)
            
            # Step 3: Apply pattern fixes
            round_fixed = 0
            for file_path, file_bugs in bugs_by_file.items():
                content = repaired_files.get(file_path, "")
                if not content:
                    continue
                
                original = content
                
                # Apply each applicable fix
                for bug in file_bugs:
                    fixer = get_fixer(bug.bug_type)
                    if fixer:
                        content, changed = fixer(content, bug)
                        if changed:
                            round_fixed += 1
                
                if content != original:
                    repaired_files[file_path] = content
            
            # Step 4: LLM repair for remaining complex bugs
            if self.llm_repairer and self.use_llm:
                # Get bugs that pattern fixers can't handle
                remaining_bugs = self.detector.scan_project(repaired_files)
                remaining_by_file: Dict[str, List[Bug]] = {}
                for bug in remaining_bugs:
                    if bug.file_path not in remaining_by_file:
                        remaining_by_file[bug.file_path] = []
                    remaining_by_file[bug.file_path].append(bug)
                
                llm_repaired = self.llm_repairer.repair_batch(
                    repaired_files, remaining_by_file
                )
                
                for file_path, content in llm_repaired.items():
                    repaired_files[file_path] = content
                    round_fixed += 1
            
            all_bugs_fixed += round_fixed
            print(f"      Fixed: {round_fixed} bugs")
            
            if round_fixed == 0:
                print(f"      No more fixes possible in this round")
                break
                
        # Phase 9: Log successful fixes to Bug Memory
        if self.chroma_client and all_bugs_fixed > 0:
            import uuid
            try:
                self.chroma_client.collections["bug_memory"].add(
                    ids=[str(uuid.uuid4())],
                    documents=[f"Repaired {all_bugs_fixed} bugs in {len(repaired_files)} files"],
                    metadatas=[{"success": True}]
                )
                logger.info(f"Logged {all_bugs_fixed} fixes to Bug Memory.")
            except BaseException as e:
                logger.warning(f"Could not log to bug_memory: {e}")
        
        # Final check
        final_bugs = self.detector.scan_project(repaired_files)
        final_summary = self.detector.get_bug_summary(final_bugs)
        
        result = RepairResult(
            success=final_summary.get("by_severity", {}).get("critical", 0) == 0,
            files_repaired=len(repaired_files),
            bugs_found=all_bugs_fixed + final_summary["total"],
            bugs_fixed=all_bugs_fixed,
            bugs_remaining=final_summary["total"],
            repair_rounds=total_rounds,
            repaired_files=repaired_files,
            unfixable_bugs=[b for b in final_bugs if b.severity == "critical"],
            report={
                "rounds": total_rounds,
                "initial_bugs": all_bugs_fixed + final_summary["total"],
                "bugs_fixed": all_bugs_fixed,
                "bugs_remaining": final_summary["total"],
                "success_rate": (
                    all_bugs_fixed / max(all_bugs_fixed + final_summary["total"], 1) * 100
                ),
                "by_severity": final_summary.get("by_severity", {}),
                "by_type": final_summary.get("by_type", {})
            }
        )
        
        print(f"\n   --- Repair Complete ---")
        print(f"   Rounds: {total_rounds}")
        print(f"   Fixed: {all_bugs_fixed}")
        print(f"   Remaining: {final_summary['total']}")
        print(f"   Success: {'Yes' if result.success else 'No'}")
        print("=" * 60)
        
        return result


# ---- Quick repair function ----

def quick_repair(files: Dict[str, str]) -> Dict[str, str]:
    """Quick repair without LLM (pattern fixes only)"""
    engine = RepairEngine(use_llm=False, max_rounds=1)
    result = engine.repair_project(files)
    return result.repaired_files


# ---- Test ----

def test_repair_engine():
    """Test the repair engine"""
    
    print("\n" + "=" * 60)
    print("🧪 REPAIR ENGINE TEST")
    print("=" * 60)
    
    # Create test files with known bugs
    test_files = {
        "src/components/Broken.tsx": """
import React from 'react';

export function BrokenComponent() {
  const items = [1, 2, 3];
  
  return (
    <div className="p-4">
      <h1>Broken Component</h1>
      <button onClick={{() => alert('clicked')}}>
        Click me
      </button>
      <ul>
        {items.map(item => (
          <li>{item}</li>
        ))}
      </ul>
      <UnclosedDiv>
        <p>This div is not closed
    </div>
  );
}
""",
        "src/components/Empty.tsx": "",
        "src/components/NoExport.tsx": """
import React from 'react';

function NoExportComponent() {
  return <div>I have no export</div>;
}
""",
    }
    
    engine = RepairEngine(use_llm=False, max_rounds=2)
    result = engine.repair_project(test_files)
    
    print(f"\n   Repaired files:")
    for path in result.repaired_files:
        print(f"      {path}")
    
    print(f"\n   Bugs found: {result.bugs_found}")
    print(f"   Bugs fixed: {result.bugs_fixed}")
    print(f"   Bugs remaining: {result.bugs_remaining}")
    print(f"   Success rate: {result.report['success_rate']:.0f}%")
    
    # Show a repaired file
    if "src/components/Broken.tsx" in result.repaired_files:
        print(f"\n   Repaired Broken.tsx (first 300 chars):")
        print(f"   {result.repaired_files['src/components/Broken.tsx'][:300]}...")
    
    print("\n✅ Repair Engine test complete")
    
    return result


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_repair_engine()