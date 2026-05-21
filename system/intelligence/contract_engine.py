"""
NOVARYX - Static Type Contract Engine
Extracts and injects TypeScript interfaces/contracts across modules.
"""

import re
import logging
from typing import Dict, List, Set

logger = logging.getLogger("novaryx.contract_engine")

class ContractEngine:
    """
    Manages cross-module interface contracts.
    
    Flow:
    1. Parse generated module for 'export interface' or 'export type'.
    2. Store these in a registry.
    3. Inject these contracts into the prompt context of dependent modules.
    """
    
    def __init__(self):
        # Simplified regex for interface/type extraction
        self.interface_pattern = re.compile(r"export\s+(interface|type)\s+(\w+)\s*\{?[^}]*\}?", re.MULTILINE)
        self.registry: Dict[str, str] = {} # {module_id: "concatenated_contracts"}
        
    def extract_contracts(self, module_id: str, files: Dict[str, str]):
        """
        Extract all exported interfaces/types from a set of files.
        """
        contracts = []
        for path, content in files.items():
            if not path.endswith((".tsx", ".ts")):
                continue
                
            matches = self.interface_pattern.findall(content)
            for m in matches:
                # Reconstruct the full interface block (heuristic)
                # In a real system, we'd use a proper parser, but this is a good first step.
                start_ptr = content.find(f"export {m[0]} {m[1]}")
                if start_ptr != -1:
                    # Find matching closing brace
                    depth = 0
                    found_start = False
                    end_ptr = start_ptr
                    for i in range(start_ptr, len(content)):
                        if content[i] == "{":
                            depth += 1
                            found_start = True
                        elif content[i] == "}":
                            depth -= 1
                        
                        if found_start and depth == 0:
                            end_ptr = i + 1
                            break
                    
                    if end_ptr > start_ptr:
                        contracts.append(content[start_ptr:end_ptr])
                        
        if contracts:
            self.registry[module_id] = "\n\n".join(contracts)
            logger.info(f"Extracted {len(contracts)} contracts from {module_id}")

    def get_injected_context(self, dependencies: List[str]) -> str:
        """
        Get a concatenated string of contracts for the given dependencies.
        """
        context = []
        for dep in dependencies:
            if dep in self.registry:
                context.append(f"// Contracts from {dep}:\n{self.registry[dep]}")
                
        if not context:
            return ""
            
        return "\n\n=== VERIFIED ARCHITECTURAL CONTRACTS ===\n" + "\n\n".join(context) + "\n========================================\n"
