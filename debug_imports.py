import sys
import os

print(f"Python version: {sys.version}")
print(f"Current dict: {dict}")

try:
    print("\nImporting stack_profiles...")
    from system.intelligence import stack_profiles
    print("✅ stack_profiles imported")
    print(f"Dict in stack_profiles: {getattr(stack_profiles, 'Dict', 'MISSING')}")
except Exception:
    import traceback
    traceback.print_exc()

try:
    print("\nImporting rule_engine...")
    from system.intelligence import rule_engine
    print("✅ rule_engine imported")
    print(f"Dict in rule_engine: {getattr(rule_engine, 'Dict', 'MISSING')}")
except Exception:
    import traceback
    traceback.print_exc()

try:
    print("\nImporting bug_detector...")
    from system.repair import bug_detector
    print("✅ bug_detector imported")
    print(f"Dict in bug_detector: {getattr(bug_detector, 'Dict', 'MISSING')}")
except Exception:
    import traceback
    traceback.print_exc()

try:
    print("\nImporting surgical_repair...")
    from system.repair import surgical_repair
    print("✅ surgical_repair imported")
    print(f"Dict in surgical_repair: {getattr(surgical_repair, 'Dict', 'MISSING')}")
except Exception:
    import traceback
    traceback.print_exc()
