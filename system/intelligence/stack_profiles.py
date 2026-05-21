from typing import Dict, Any, List

# Semantic Version Compatibility Matrix
# Maps "Major Package version" to "Compatible Peer versions"
VERSION_MAP = {
    "vite@5": {
        "@vitejs/plugin-react": "^4.2.1",
        "@types/react": "^18.2.0",
        "postcss": "^8.4.0"
    },
    "vite@4": {
        "@vitejs/plugin-react": "^3.1.0"
    }
}

VITE_REACT_STACK = {
    "dependencies": {
        "react": "^18.2.0",
        "react-dom": "^18.2.0",
        "framer-motion": "^11.0.0",
        "lucide-react": "^0.344.0",
        "clsx": "^2.1.0",
        "tailwind-merge": "^2.2.1"
    },
    "devDependencies": {
        "vite": "^5.1.0",
        "@vitejs/plugin-react": "^4.2.1",
        "typescript": "^5.3.3",
        "tailwindcss": "^3.4.1",
        "postcss": "^8.4.35",
        "autoprefixer": "^10.4.17",
        "@types/react": "^18.2.55",
        "@types/react-dom": "^18.2.19"
    }
}

NEXTJS_STACK = {
    "dependencies": {
        "next": "^14.1.0",
        "react": "^18.2.0",
        "react-dom": "^18.2.0",
        "framer-motion": "^11.0.0",
        "lucide-react": "^0.344.0",
        "next-auth": "^4.24.5",
        "clsx": "^2.1.0",
        "tailwind-merge": "^2.2.1"
    },
    "devDependencies": {
        "typescript": "^5.3.3",
        "tailwindcss": "^3.4.1",
        "postcss": "^8.4.35",
        "autoprefixer": "^10.4.17",
        "@types/node": "^20.11.19",
        "@types/react": "^18.2.55",
        "@types/react-dom": "^18.2.19"
    }
}

STACK_PROFILES: Dict[str, Dict[str, Any]] = {
    "vite_react": VITE_REACT_STACK,
    "nextjs": NEXTJS_STACK
}

def resolve_compatible_version(pkg_name: str, parent_pkg: str, parent_version: str) -> str:
    """Find a version of pkg_name compatible with parent_pkg at parent_version."""
    parent_key = f"{parent_pkg}@{parent_version.split('.')[0].replace('^', '').replace('~', '')}"
    if parent_key in VERSION_MAP:
        return VERSION_MAP[parent_key].get(pkg_name, "latest")
    return "latest"

def get_stack_profile(project_type: str) -> Dict[str, Any]:
    """Return the profile for the given project type, defaulting to Vite/React."""
    if "next" in project_type.lower():
        return STACK_PROFILES["nextjs"]
    return STACK_PROFILES["vite_react"]
