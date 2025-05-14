# Root-level CLI script for fintech_developer CLI commands
 # Module-level orchestrator placeholder for data_scientist CLI monkeypatch
orch = None
import sys
from fintech_developer.cli import main

if __name__ == "__main__":
    # Delegate to fintech_developer CLI
    main()