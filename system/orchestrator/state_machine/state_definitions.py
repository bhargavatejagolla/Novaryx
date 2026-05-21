"""
NOVARYX - State Definitions
All valid states, transitions, and metadata for the generation system.
"""

from enum import Enum
from typing import Dict, List, Set, Tuple


class GenerationState(Enum):
    """Complete set of system states"""
    
    # Initial states
    IDLE = "idle"
    INITIALIZING = "initializing"
    READY = "ready"
    
    # Pipeline states
    PARSING_PROMPT = "parsing_prompt"
    CLASSIFYING_PROJECT = "classifying_project"
    PLANNING_ARCHITECTURE = "planning_architecture"
    RETRIEVING_TEMPLATES = "retrieving_templates"
    RETRIEVING_COMPONENTS = "retrieving_components"
    GENERATING_PAGES = "generating_pages"
    GENERATING_BACKEND = "generating_backend"
    GENERATING_COMPONENTS = "generating_components"
    ASSEMBLING_PROJECT = "assembling_project"
    
    # Verification states
    VERIFYING_SYNTAX = "verifying_syntax"
    VERIFYING_IMPORTS = "verifying_imports"
    VERIFYING_TYPES = "verifying_types"
    VERIFYING_ROUTES = "verifying_routes"
    VERIFYING_BUILD = "verifying_build"
    
    # Repair states
    DIAGNOSING = "diagnosing"
    REPAIRING = "repairing"
    RETRYING = "retrying"
    
    # Packaging states
    PACKAGING = "packaging"
    GENERATING_DOCS = "generating_docs"
    DEPLOYING_LOCAL = "deploying_local"
    
    # Terminal states
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    
    # System states
    PAUSED = "paused"
    RECOVERING = "recovering"
    ROLLING_BACK = "rolling_back"
    MAINTENANCE = "maintenance"


# ---- Valid State Transitions ----
# Defines exactly which states can transition to which other states

VALID_TRANSITIONS: Dict[GenerationState, List[GenerationState]] = {
    
    # Startup flow
    GenerationState.IDLE: [
        GenerationState.INITIALIZING
    ],
    GenerationState.INITIALIZING: [
        GenerationState.READY,
        GenerationState.FAILED
    ],
    GenerationState.READY: [
        GenerationState.PARSING_PROMPT,
        GenerationState.IDLE,
        GenerationState.MAINTENANCE
    ],
    
    # Pipeline flow
    GenerationState.PARSING_PROMPT: [
        GenerationState.CLASSIFYING_PROJECT,
        GenerationState.FAILED,
        GenerationState.CANCELLED
    ],
    GenerationState.CLASSIFYING_PROJECT: [
        GenerationState.PLANNING_ARCHITECTURE,
        GenerationState.FAILED
    ],
    GenerationState.PLANNING_ARCHITECTURE: [
        GenerationState.RETRIEVING_TEMPLATES,
        GenerationState.FAILED
    ],
    GenerationState.RETRIEVING_TEMPLATES: [
        GenerationState.RETRIEVING_COMPONENTS,
        GenerationState.GENERATING_PAGES,
        GenerationState.FAILED
    ],
    GenerationState.RETRIEVING_COMPONENTS: [
        GenerationState.GENERATING_PAGES,
        GenerationState.FAILED
    ],
    GenerationState.GENERATING_PAGES: [
        GenerationState.GENERATING_BACKEND,
        GenerationState.GENERATING_COMPONENTS,
        GenerationState.ASSEMBLING_PROJECT,
        GenerationState.FAILED
    ],
    GenerationState.GENERATING_BACKEND: [
        GenerationState.GENERATING_COMPONENTS,
        GenerationState.ASSEMBLING_PROJECT,
        GenerationState.FAILED
    ],
    GenerationState.GENERATING_COMPONENTS: [
        GenerationState.ASSEMBLING_PROJECT,
        GenerationState.FAILED
    ],
    GenerationState.ASSEMBLING_PROJECT: [
        GenerationState.VERIFYING_SYNTAX,
        GenerationState.FAILED
    ],
    
    # Verification flow
    GenerationState.VERIFYING_SYNTAX: [
        GenerationState.VERIFYING_IMPORTS,
        GenerationState.DIAGNOSING,
        GenerationState.FAILED
    ],
    GenerationState.VERIFYING_IMPORTS: [
        GenerationState.VERIFYING_TYPES,
        GenerationState.DIAGNOSING,
        GenerationState.FAILED
    ],
    GenerationState.VERIFYING_TYPES: [
        GenerationState.VERIFYING_ROUTES,
        GenerationState.DIAGNOSING,
        GenerationState.FAILED
    ],
    GenerationState.VERIFYING_ROUTES: [
        GenerationState.VERIFYING_BUILD,
        GenerationState.DIAGNOSING,
        GenerationState.FAILED
    ],
    GenerationState.VERIFYING_BUILD: [
        GenerationState.PACKAGING,
        GenerationState.DIAGNOSING,
        GenerationState.FAILED
    ],
    
    # Repair flow
    GenerationState.DIAGNOSING: [
        GenerationState.REPAIRING,
        GenerationState.FAILED
    ],
    GenerationState.REPAIRING: [
        GenerationState.RETRYING,
        GenerationState.FAILED,
        GenerationState.ROLLING_BACK
    ],
    GenerationState.RETRYING: [
        GenerationState.GENERATING_PAGES,
        GenerationState.GENERATING_COMPONENTS,
        GenerationState.ASSEMBLING_PROJECT,
        GenerationState.VERIFYING_SYNTAX,
        GenerationState.FAILED
    ],
    
    # Packaging
    GenerationState.PACKAGING: [
        GenerationState.GENERATING_DOCS,
        GenerationState.COMPLETED,
        GenerationState.FAILED
    ],
    GenerationState.GENERATING_DOCS: [
        GenerationState.DEPLOYING_LOCAL,
        GenerationState.COMPLETED,
        GenerationState.FAILED
    ],
    GenerationState.DEPLOYING_LOCAL: [
        GenerationState.COMPLETED,
        GenerationState.FAILED
    ],
    
    # Terminal states (no outgoing transitions normally)
    GenerationState.COMPLETED: [],
    GenerationState.CANCELLED: [],
    GenerationState.TIMED_OUT: [],
    
    # Failure recovery
    GenerationState.FAILED: [
        GenerationState.DIAGNOSING,
        GenerationState.ROLLING_BACK,
        GenerationState.IDLE,
        GenerationState.RECOVERING
    ],
    
    # System states
    GenerationState.PAUSED: [
        GenerationState.RECOVERING,
        GenerationState.CANCELLED
    ],
    GenerationState.RECOVERING: [
        GenerationState.RETRYING,
        GenerationState.FAILED,
        GenerationState.READY
    ],
    GenerationState.ROLLING_BACK: [
        GenerationState.IDLE,
        GenerationState.READY,
        GenerationState.FAILED
    ],
    GenerationState.MAINTENANCE: [
        GenerationState.IDLE
    ],
}


# ---- Terminal States ----
# States where the system stops (no automatic transitions)

TERMINAL_STATES: Set[GenerationState] = {
    GenerationState.COMPLETED,
    GenerationState.FAILED,
    GenerationState.CANCELLED,
    GenerationState.TIMED_OUT
}


# ---- Recoverable States ----
# States from which we can attempt recovery

RECOVERABLE_STATES: Set[GenerationState] = {
    GenerationState.FAILED,
    GenerationState.TIMED_OUT,
    GenerationState.PAUSED
}


# ---- State Metadata ----
# Descriptions and properties for each state

STATE_METADATA: Dict[GenerationState, Dict] = {
    GenerationState.IDLE: {
        "phase": "system",
        "description": "System is idle, waiting for input",
        "is_blocking": False,
        "timeout_seconds": None
    },
    GenerationState.INITIALIZING: {
        "phase": "system",
        "description": "Initializing all subsystems",
        "is_blocking": True,
        "timeout_seconds": 60
    },
    GenerationState.READY: {
        "phase": "system",
        "description": "Ready to accept prompts",
        "is_blocking": False,
        "timeout_seconds": None
    },
    GenerationState.PARSING_PROMPT: {
        "phase": "parsing",
        "description": "Parsing user prompt for requirements",
        "is_blocking": True,
        "timeout_seconds": 30
    },
    GenerationState.CLASSIFYING_PROJECT: {
        "phase": "planning",
        "description": "Determining project type",
        "is_blocking": True,
        "timeout_seconds": 30
    },
    GenerationState.PLANNING_ARCHITECTURE: {
        "phase": "planning",
        "description": "Designing system architecture",
        "is_blocking": True,
        "timeout_seconds": 120
    },
    GenerationState.RETRIEVING_TEMPLATES: {
        "phase": "retrieval",
        "description": "Finding matching templates from RAG",
        "is_blocking": True,
        "timeout_seconds": 30
    },
    GenerationState.RETRIEVING_COMPONENTS: {
        "phase": "retrieval",
        "description": "Finding matching components",
        "is_blocking": True,
        "timeout_seconds": 30
    },
    GenerationState.GENERATING_PAGES: {
        "phase": "generation",
        "description": "Generating frontend pages",
        "is_blocking": True,
        "timeout_seconds": 300
    },
    GenerationState.GENERATING_BACKEND: {
        "phase": "generation",
        "description": "Generating backend schema",
        "is_blocking": True,
        "timeout_seconds": 120
    },
    GenerationState.GENERATING_COMPONENTS: {
        "phase": "generation",
        "description": "Generating individual components",
        "is_blocking": True,
        "timeout_seconds": 300
    },
    GenerationState.ASSEMBLING_PROJECT: {
        "phase": "generation",
        "description": "Assembling final project structure",
        "is_blocking": True,
        "timeout_seconds": 60
    },
    GenerationState.VERIFYING_SYNTAX: {
        "phase": "verification",
        "description": "Checking syntax of all files",
        "is_blocking": True,
        "timeout_seconds": 60
    },
    GenerationState.VERIFYING_IMPORTS: {
        "phase": "verification",
        "description": "Validating all imports resolve",
        "is_blocking": True,
        "timeout_seconds": 60
    },
    GenerationState.VERIFYING_TYPES: {
        "phase": "verification",
        "description": "TypeScript type checking",
        "is_blocking": True,
        "timeout_seconds": 120
    },
    GenerationState.VERIFYING_ROUTES: {
        "phase": "verification",
        "description": "Validating route connections",
        "is_blocking": True,
        "timeout_seconds": 30
    },
    GenerationState.VERIFYING_BUILD: {
        "phase": "verification",
        "description": "Running build check",
        "is_blocking": True,
        "timeout_seconds": 180
    },
    GenerationState.DIAGNOSING: {
        "phase": "repair",
        "description": "Diagnosing issues",
        "is_blocking": True,
        "timeout_seconds": 60
    },
    GenerationState.REPAIRING: {
        "phase": "repair",
        "description": "Repairing detected issues",
        "is_blocking": True,
        "timeout_seconds": 180
    },
    GenerationState.RETRYING: {
        "phase": "repair",
        "description": "Retrying failed step",
        "is_blocking": True,
        "timeout_seconds": 300
    },
    GenerationState.PACKAGING: {
        "phase": "packaging",
        "description": "Creating final package",
        "is_blocking": True,
        "timeout_seconds": 60
    },
    GenerationState.GENERATING_DOCS: {
        "phase": "packaging",
        "description": "Generating documentation",
        "is_blocking": True,
        "timeout_seconds": 60
    },
    GenerationState.DEPLOYING_LOCAL: {
        "phase": "deployment",
        "description": "Deploying to local environment",
        "is_blocking": True,
        "timeout_seconds": 120
    },
    GenerationState.COMPLETED: {
        "phase": "terminal",
        "description": "Generation completed successfully",
        "is_blocking": False,
        "timeout_seconds": None
    },
    GenerationState.FAILED: {
        "phase": "terminal",
        "description": "Generation failed",
        "is_blocking": False,
        "timeout_seconds": None
    },
    GenerationState.CANCELLED: {
        "phase": "terminal",
        "description": "Cancelled by user",
        "is_blocking": False,
        "timeout_seconds": None
    },
    GenerationState.TIMED_OUT: {
        "phase": "terminal",
        "description": "Timed out",
        "is_blocking": False,
        "timeout_seconds": None
    },
    GenerationState.PAUSED: {
        "phase": "system",
        "description": "System paused",
        "is_blocking": True,
        "timeout_seconds": None
    },
    GenerationState.RECOVERING: {
        "phase": "system",
        "description": "Recovering from previous state",
        "is_blocking": True,
        "timeout_seconds": 120
    },
    GenerationState.ROLLING_BACK: {
        "phase": "system",
        "description": "Rolling back to safe state",
        "is_blocking": True,
        "timeout_seconds": 60
    },
    GenerationState.MAINTENANCE: {
        "phase": "system",
        "description": "System maintenance mode",
        "is_blocking": True,
        "timeout_seconds": None
    },
}


def is_valid_transition(from_state: GenerationState, to_state: GenerationState) -> bool:
    """Check if a state transition is valid"""
    valid_targets = VALID_TRANSITIONS.get(from_state, [])
    return to_state in valid_targets


def get_allowed_transitions(state: GenerationState) -> List[GenerationState]:
    """Get all states we can transition to from current state"""
    return VALID_TRANSITIONS.get(state, [])


def get_state_metadata(state: GenerationState) -> Dict:
    """Get metadata for a state"""
    return STATE_METADATA.get(state, {
        "phase": "unknown",
        "description": "Unknown state",
        "is_blocking": False,
        "timeout_seconds": None
    })


def get_phase_states(phase: str) -> List[GenerationState]:
    """Get all states belonging to a phase"""
    return [
        state for state, meta in STATE_METADATA.items()
        if meta.get("phase") == phase
    ]