
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from system.inference.provider_factory import get_provider, list_available_providers

def verify_priorities():
    print("--- Verifying Provider Priorities ---")
    providers = list_available_providers()
    for p in providers:
        print(f"Provider: {p['name']}, Priority: {p['priority']}, Available: {p['available']}")
    
    try:
        active = get_provider()
        print(f"\nActive Provider: {active.name} (Priority: {active.priority})")
        
        # Verify Groq model
        if active.name == "groq" or any(p['name'] == "groq" and p['available'] for p in providers):
            from system.inference.groq_provider import GroqProvider
            groq = GroqProvider()
            planning_model = groq.MODEL_ROLES.get("planning")
            print(f"Groq Planning Model: {planning_model}")
            assert planning_model == "llama-3.3-70b-versatile", f"Expected llama-3.3-70b-versatile, got {planning_model}"
            assert groq.priority == 100, f"Expected Groq priority 100, got {groq.priority}"
            
        from system.inference.ollama_provider import OllamaProvider
        ollama = OllamaProvider()
        print(f"Ollama Priority: {ollama.priority}")
        assert ollama.priority == 200, f"Expected Ollama priority 200, got {ollama.priority}"
        
        print("\n[SUCCESS] Verification successful!")
        
    except Exception as e:
        print(f"\n[FAILED] Verification failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_priorities()
