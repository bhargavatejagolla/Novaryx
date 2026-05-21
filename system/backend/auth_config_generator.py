"""
NOVARYX - Auth Config Generator
Generates PocketBase auth configuration.
"""

import json


class AuthConfigGenerator:
    """Generates auth configuration for PocketBase"""
    
    @staticmethod
    def generate_auth_config(config: dict) -> str:
        """Generate auth configuration JSON"""
        return json.dumps(config, indent=2)
