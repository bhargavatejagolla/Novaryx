import sys, os

# Setup path and env
sys.path.insert(0, str(__file__).rsplit('/', 1)[0] if '/' in __file__ else '.')
# Load from environment variables (does not hardcode raw keys)
os.environ.setdefault('GROQ_API_KEY', os.environ.get('GROQ_API_KEY', ''))
os.environ.setdefault('GROQ_MODEL_GENERATION', 'llama-3.1-8b-instant')
os.environ.setdefault('GROQ_MODEL_PLANNING', 'deepseek-r1-distill-llama-70b')

from system.inference.provider_factory import list_available_providers, get_provider, reset_providers

reset_providers()
providers = list_available_providers()
print("\n=== Provider Status ===")
for p in providers:
    status = "ONLINE" if p["available"] else "OFFLINE"
    print(f"  {p['name']:<10} priority={p['priority']}  {status}")

print("\n=== Active Provider ===")
try:
    active = get_provider()
    print(f"  ACTIVE: {active.name} (priority={active.priority})")
    models = active.get_available_models()
    print(f"  Models: {models[:5]}")
except RuntimeError as e:
    print(f"  ERROR: {e}")

print("\n=== Quick Generation Test (Groq) ===")
try:
    from system.inference.groq_provider import GroqProvider
    g = GroqProvider()
    if g.is_available():
        r = g.generate("Say: NOVARYX Groq test OK", max_tokens=20, role="default")
        print(f"  Result: {r.text.strip()[:80]}")
        print(f"  Tokens: {r.tokens_used}, Time: {r.generation_time_ms:.0f}ms")
    else:
        print("  Groq not available")
except Exception as e:
    print(f"  Error: {e}")
