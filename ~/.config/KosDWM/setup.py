#!/usr/bin/env python3
"""
KosDWM Setup
============

Standard Python package setup for pip installation.

Usage:
    pip install .                    # Install KosDWM
    pip install -e .                 # Install in development mode
    pip uninstall kosdwm             # Remove KosDWM
"""

from setuptools import setup, find_packages
from pathlib import Path


# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""


setup(
    name="kosdwm",
    version="1.0.0",
    description="Dynamic Window Manager with Python Gadgets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="KosDWM Team",
    url="https://github.com/yourusername/kosdwm",
    
    # Packages
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Scripts
    entry_points={
        "console_scripts": [
            "kosdwm=kosdwm:main",
            "kosdwm-panel=panel:main",
        ],
    },
    
    # Data files
    package_data={
        "": ["*.py", "*.md", "*.txt"],
    },
    
    # Dependencies
    python_requires=">=3.7",
    install_requires=[
        # Core dependencies (tkinter is usually system-installed)
    ],
    extras_require={
        "api": ["flask>=1.0", "flask-cors"],
        "notifications": ["plyer"],  # For cross-platform notifications
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Desktop Environment :: Window Managers",
    ],
    
    # Keywords
    keywords="window-manager dwm tiling x11 gadgets python",
)
