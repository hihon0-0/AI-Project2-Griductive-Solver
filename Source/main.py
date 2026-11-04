"""Main entry point for Griductive Solver."""
import sys
import os

# Add Source directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 60)
    print("   GRIDUCTIVE SOLVER — CSC14003 AI PROJECT 2 (HCMUS)   ")
    print("=" * 60)
    print("Running initial setup check...")
    print("Modules organized for 5 team members:")
    print(" - TV1: Core DPLL SAT Solver (Source/core/dpll.py)")
    print(" - TV2: CNF Encoder & Semantics (Source/core/encoder.py)")
    print(" - TV3: Game Engine & Data (Source/engine/engine.py)")
    print(" - TV4: Deductive Logic Agent (Source/agent/agent.py)")
    print(" - TV5: GUI & Animation (Source/gui/app.py)")
    print("\nTo launch GUI application:")
    print("   python Source/gui/app.py")
    print("=" * 60)

if __name__ == '__main__':
    main()
