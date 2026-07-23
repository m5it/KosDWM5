"""
Version Module for KosDWM
=========================

Provides version information from AUTOVERSION.py
"""

import sys
from pathlib import Path


def get_version():
    """Get current KosDWM version."""
    # Look for AUTOVERSION.py in parent directories
    current = Path(__file__).parent
    for parent in [current.parent] + list(current.parents):
        version_file = parent / "AUTOVERSION.py"
        if version_file.exists():
            # Execute the file to get VERSION
            namespace = {}
            exec(open(version_file).read(), namespace)
            return namespace.get("VERSION", "unknown")
    return "unknown"


def get_version_info():
    """Get detailed version info."""
    version = get_version()
    return {
        "version": version,
        "name": "KosDWM",
        "full": f"KosDWM {version}"
    }


if __name__ == "__main__":
    print(get_version())
