#!/usr/bin/env python3
"""
NOVARYX - Main Generation Interface
THE entry point for the entire system.

Usage:
  python novaryx_generate.py "Build a dark SaaS dashboard with analytics"
  python novaryx_generate.py --prompt "Create a landing page" --name "MyStartup"
  python novaryx_generate.py --interactive
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from system.templates.dynamic.pipeline import novaryx_generate, write_project_to_disk


def main():
    parser = argparse.ArgumentParser(
        description="NOVARYX - AI-Powered Application Builder",
        epilog="Example: python novaryx_generate.py 'Build a dark purple SaaS dashboard with analytics'"
    )
    
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Description of the project to build"
    )
    parser.add_argument(
        "--prompt", "-p",
        dest="prompt_flag",
        help="Project description (alternative)"
    )
    parser.add_argument(
        "--name", "-n",
        default="",
        help="Project name"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output directory"
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM for faster generation"
    )
    parser.add_argument(
        "--no-rag",
        action="store_true",
        help="Disable RAG retrieval"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive mode"
    )
    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Show version"
    )
    
    args = parser.parse_args()
    
    # Version
    if args.version:
        print("NOVARYX v0.10.0 - AI-Powered Application Builder")
        return
    
    # Interactive mode
    if args.interactive:
        print("\n" + "=" * 60)
        print("NOVARYX INTERACTIVE MODE")
        print("=" * 60)
        print("Describe what you want to build...")
        print()
        prompt = input("> ")
        project_name = input("Project name (optional): ").strip()
        
        if not prompt:
            print("No prompt provided. Exiting.")
            return
        
        result = novaryx_generate(
            prompt=prompt,
            project_name=project_name,
            use_llm=not args.no_llm,
            use_rag=not args.no_rag
        )
        
        write_project_to_disk(result, args.output)
        return
    
    # Get prompt
    prompt = args.prompt or args.prompt_flag
    
    if not prompt:
        parser.print_help()
        print("\nExample: python novaryx_generate.py 'Build a dark purple SaaS dashboard'")
        return
    
    # Generate
    print(f"\nGenerating: {prompt[:80]}...")
    
    result = novaryx_generate(
        prompt=prompt,
        project_name=args.name,
        use_llm=not args.no_llm,
        use_rag=not args.no_rag
    )
    
    # Write to disk
    write_project_to_disk(result, args.output)


if __name__ == "__main__":
    main()
