#!/usr/bin/env python3
"""
Remove file from Git history
============================
Removes a file completely from Git history using git filter-repo or filter-branch.
"""

import subprocess
import sys
import os


def run(cmd, check=True):
    """Run a shell command."""
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr and check:
        print(result.stderr, file=sys.stderr)
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python remove_from_history.py <filename>")
        print("Example: python remove_from_history.py run.out")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    # Check for unstaged changes
    result = run("git status --porcelain", check=False)
    if result.stdout.strip():
        print("You have unstaged changes. Stashing them first...")
        run("git stash")
        stashed = True
    else:
        stashed = False
    
    # Try git-filter-repo first (better tool)
    result = run("which git-filter-repo", check=False)
    if result.returncode == 0:
        print(f"Using git-filter-repo to remove {filename}...")
        run(f"git filter-repo --strip-blobs-bigger-than 100M --force")
    else:
        print(f"Using git filter-branch to remove {filename}...")
        print("This may take a while...")
        
        # Use filter-branch
        run(f'git filter-branch --force --index-filter "git rm --cached --ignore-unmatch {filename}" --prune-empty --tag-name-filter cat -- --all')
        
        # Clean up
        run("rm -rf .git/refs/originals/")
        run("git reflog expire --expire=now --all")
        run("git gc --prune=now --aggressive")
    
    # Restore stashed changes
    if stashed:
        print("Restoring stashed changes...")
        run("git stash pop")
    
    print(f"\n✓ {filename} removed from history!")
    print("Now run: git push --force github master")


if __name__ == "__main__":
    main()
