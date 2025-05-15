#!/usr/bin/env python3
"""
Demo script for the unified task manager CLI with persistent storage.

This script demonstrates key features of the task manager in a single session.
"""

import os
import sys
import uuid
import subprocess
from datetime import datetime, timedelta


def run_command(command):
    """Run a CLI command and print the result."""
    print(f"\n\033[1;34m> {command}\033[0m")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(f"\033[1;31mError: {result.stderr.strip()}\033[0m")
    return result.stdout.strip()


def main():
    """Run the demo."""
    script_path = "./cli_persistent.py"
    
    # Ensure the script exists and is executable
    if not os.path.isfile(script_path):
        print(f"Error: {script_path} not found")
        return 1
    
    print("\033[1;32m=== Unified Task Manager Demo ===\033[0m")
    
    # Show help
    run_command(f"{script_path} --help")
    
    # Create tasks
    print("\n\033[1;32m=== Creating Tasks ===\033[0m")
    
    # Create a generic task
    generic_task_id = run_command(
        f"{script_path} create "
        f"--title 'Setup Development Environment' "
        f"--description 'Configure development tools and dependencies' "
        f"--priority medium "
        f"--tags 'setup,dev,tools'"
    ).split("ID: ")[-1]
    
    # Create a research task
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    research_task_id = run_command(
        f"{script_path} create "
        f"--title 'Literature Review' "
        f"--description 'Review papers on machine learning techniques' "
        f"--type research "
        f"--priority high "
        f"--estimated-hours 8 "
        f"--due {tomorrow} "
        f"--tags 'research,ML,literature'"
    ).split("ID: ")[-1]
    
    # Create a subtask for research
    research_subtask_id = run_command(
        f"{script_path} create "
        f"--title 'Summarize Key Findings' "
        f"--description 'Write summary of key papers' "
        f"--type research "
        f"--parent {research_task_id} "
        f"--estimated-hours 3"
    ).split("ID: ")[-1]
    
    # Create a security task
    security_task_id = run_command(
        f"{script_path} create "
        f"--title 'SQL Injection Vulnerability' "
        f"--description 'Fix SQL injection vulnerability in login form' "
        f"--type security "
        f"--priority critical "
        f"--severity 'Critical' "
        f"--affected-systems 'auth-service,user-api' "
        f"--discovered-by 'Security Team' "
        f"--tags 'security,vulnerability,critical'"
    ).split("ID: ")[-1]
    
    # List all tasks
    print("\n\033[1;32m=== Listing Tasks ===\033[0m")
    run_command(f"{script_path} list")
    
    # List by type
    print("\n\033[1;32m=== Listing Research Tasks ===\033[0m")
    run_command(f"{script_path} list --type research")
    
    # List by status
    print("\n\033[1;32m=== Listing Planned Tasks ===\033[0m")
    run_command(f"{script_path} list --status planned")
    
    # List by priority
    print("\n\033[1;32m=== Listing Critical Tasks ===\033[0m")
    run_command(f"{script_path} list --priority critical")
    
    # List by tag
    print("\n\033[1;32m=== Listing Security Tasks by Tag ===\033[0m")
    run_command(f"{script_path} list --tag security")
    
    # Get task details
    print("\n\033[1;32m=== Task Details ===\033[0m")
    run_command(f"{script_path} get {research_task_id}")
    
    # Get JSON formatted output
    print("\n\033[1;32m=== JSON Output ===\033[0m")
    run_command(f"{script_path} get {security_task_id} --json")
    
    # Update tasks
    print("\n\033[1;32m=== Updating Tasks ===\033[0m")
    run_command(
        f"{script_path} update {generic_task_id} "
        f"--status in_progress"
    )
    
    # Add note
    print("\n\033[1;32m=== Adding Notes ===\033[0m")
    run_command(
        f"{script_path} note {research_task_id} "
        f"'Found 5 relevant papers to review'"
    )
    
    # Add tag
    print("\n\033[1;32m=== Adding Tags ===\033[0m")
    run_command(
        f"{script_path} add-tag {security_task_id} "
        f"urgent"
    )
    
    # Remove tag
    print("\n\033[1;32m=== Removing Tags ===\033[0m")
    run_command(
        f"{script_path} remove-tag {security_task_id} "
        f"vulnerability"
    )
    
    # Complete a task
    print("\n\033[1;32m=== Completing Tasks ===\033[0m")
    run_command(
        f"{script_path} update {generic_task_id} "
        f"--status completed"
    )
    
    # Final task listing
    print("\n\033[1;32m=== Final Task Listing ===\033[0m")
    run_command(f"{script_path} list")
    
    # Delete a task
    print("\n\033[1;32m=== Deleting Tasks ===\033[0m")
    run_command(f"{script_path} delete {research_subtask_id}")
    
    # Show final state
    print("\n\033[1;32m=== Final State ===\033[0m")
    run_command(f"{script_path} list")
    
    print("\n\033[1;32m=== Demo Completed ===\033[0m")
    return 0


if __name__ == "__main__":
    sys.exit(main())