#!/usr/bin/env python3
"""
KosDWM Gadget Loader Template
=============================

Copy this at the top of your gadget to ensure it can find KosDWM modules
regardless of where KosDWM is installed.

Usage:
    Copy the sys.path setup from below into your gadget file.
"""

import sys
from pathlib import Path

# Method 1: Use KOSDWM_HOME environment variable (recommended)
if 'KOSDWM_HOME' in __import__('os').environ:
    KOSDWM_PATH = Path(__import__('os').environ['KOSDWM_HOME'])
else:
    # Method 2: Common installation paths
    home = Path.home()
    possible_paths = [
        home / ".local" / "share" / "kosdwm",
        home / "KosDWM",
        home / "kosdwm",
        Path("/usr/local/share/kosdwm"),
        Path("/opt/kosdwm"),
    ]
    
    # Method 3: Check if KosDWM is in parent directories
    current = Path(__file__).resolve()
    for parent in [current.parent] + list(current.parents):
        if (parent / "src" / "kosdwm.py").exists():
            KOSDWM_PATH = parent
            break
    else:
        # Use first existing path or default
        KOSDWM_PATH = next((p for p in possible_paths if p.exists()), possible_paths[0])

# Add KosDWM src to Python path
sys.path.insert(0, str(KOSDWM_PATH / "src"))

# Now you can import KosDWM modules
# from gadgets import GadgetBase
# from kosdwm import ...
