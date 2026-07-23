#!/usr/bin/env python3
"""
KosDWM Diagnostic Tool
======================

Checks if KosDWM is properly installed and helps troubleshoot gadget issues.
Run with: python kosdwm_diagnose.py
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN} {text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")

def print_success(text):
    print(f"{Colors.GREEN}✓{Colors.RESET} {text}")

def print_error(text):
    print(f"{Colors.RED}✗{Colors.RESET} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {text}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {text}")

def check_environment():
    """Check environment variables and basic setup."""
    print_header("ENVIRONMENT CHECK")
    
    # Check KOSDWM_HOME
    kosdwm_home = os.environ.get('KOSDWM_HOME')
    if kosdwm_home:
        print_success(f"KOSDWM_HOME is set: {kosdwm_home}")
        path = Path(kosdwm_home)
        if path.exists():
            print_success(f"  Directory exists")
            if (path / "src").exists():
                print_success(f"  Has src/ subdirectory")
            else:
                print_error(f"  Missing src/ subdirectory")
        else:
            print_error(f"  Directory does NOT exist")
    else:
        print_warning("KOSDWM_HOME is NOT set")
    
    # Check Python path
    print_info(f"Python version: {sys.version}")
    
    # Check if KosDWM is in Python path
    kosdwm_in_path = any('KosDWM' in p or 'kosdwm' in p.lower() for p in sys.path)
    if kosdwm_in_path:
        print_success("KosDWM appears in sys.path")
    else:
        print_warning("KosDWM not found in sys.path")

def find_kosdwm_path():
    """Try to find KosDWM installation."""
    print_header("SEARCHING FOR KOSDWM")
    
    # Check common locations
    home = Path.home()
    locations = [
        os.environ.get('KOSDWM_HOME'),
        home / ".config" / "KosDWM" / "kosdwm_path.conf",
        home / "Projects" / "KosDWM",
        home / "workspace" / "KosDWM",
        home / "code" / "KosDWM",
        home / "KosDWM",
        home / "kosdwm",
        Path("/opt/KosDWM"),
        Path("/usr/local/share/KosDWM"),
    ]
    
    found_paths = []
    for loc in locations:
        if loc is None:
            continue
        if isinstance(loc, Path) and loc.exists():
            if loc.is_file():
                # It's a config file
                try:
                    with open(loc) as f:
                        path = Path(f.read().strip())
                        if path.exists():
                            found_paths.append(("config file", path))
                            print_success(f"Found via config file {loc}: {path}")
                except Exception as e:
                    print_error(f"Error reading {loc}: {e}")
            elif (loc / "src").exists():
                found_paths.append(("directory", loc))
                print_success(f"Found KosDWM at: {loc}")
    
    if not found_paths:
        print_error("KosDWM installation not found!")
        print_info("Searched locations:")
        for loc in locations:
            if loc:
                print_info(f"  - {loc}")
    
    return found_paths

def check_installation(kosdwm_path):
    """Check if KosDWM installation is complete."""
    print_header("INSTALLATION CHECK")
    
    required_files = [
        "run.py",
        "src/gadgets.py",
        "src/config.py",
        "src/functions.py",
    ]
    
    all_ok = True
    for file in required_files:
        full_path = kosdwm_path / file
        if full_path.exists():
            print_success(f"Found: {file}")
        else:
            print_error(f"Missing: {file}")
            all_ok = False
    
    return all_ok

def check_gadgets(kosdwm_path):
    """Check gadget configuration and files."""
    print_header("GADGET CHECK")
    
    config_dir = Path.home() / ".config" / "KosDWM"
    gadgets_dir = config_dir / "gadgets"
    
    # Check directories
    if config_dir.exists():
        print_success(f"Config directory: {config_dir}")
    else:
        print_error(f"Config directory missing: {config_dir}")
        return
    
    if gadgets_dir.exists():
        print_success(f"Gadgets directory: {gadgets_dir}")
    else:
        print_error(f"Gadgets directory missing: {gadgets_dir}")
        return
    
    # Check gadgets.json
    gadgets_json = config_dir / "gadgets.json"
    if gadgets_json.exists():
        print_success(f"Gadgets config: {gadgets_json}")
        try:
            with open(gadgets_json) as f:
                config = json.load(f)
                enabled = config.get('enabled', [])
                print_info(f"  Enabled gadgets: {enabled}")
                
                if not enabled:
                    print_warning("  No gadgets are enabled!")
                    print_info("  To enable gadgets, edit gadgets.json or use the gadget manager")
        except Exception as e:
            print_error(f"  Error reading gadgets.json: {e}")
    else:
        print_error(f"Gadgets config missing: {gadgets_json}")
    
    # Check for gadget files
    print_info("\nGadget files found:")
    gadget_files = list(gadgets_dir.glob("*.py"))
    if gadget_files:
        for gf in gadget_files:
            print_info(f"  - {gf.name}")
    else:
        print_warning("  No gadget .py files found")
    
    # Check each enabled gadget
    if gadgets_json.exists():
        try:
            with open(gadgets_json) as f:
                config = json.load(f)
                enabled = config.get('enabled', [])
                
                if enabled:
                    print_info(f"\nChecking enabled gadgets:")
                    for gadget_name in enabled:
                        gadget_file = gadgets_dir / f"{gadget_name}.py"
                        if gadget_file.exists():
                            print_success(f"  {gadget_name}: file exists")
                            # Try to check if it can import KosDWM
                            try:
                                content = gadget_file.read_text()
                                if 'KOSDWM_HOME' in content or 'find_kosdwm_path' in content:
                                    print_success(f"    Has path detection code")
                                elif "sys.path.insert" in content and "find_kosdwm_path" not in content:
                                    print_warning(f"    Has hardcoded path - may not be portable")
                            except Exception as e:
                                print_error(f"    Error reading: {e}")
                        else:
                            print_error(f"  {gadget_name}: file NOT found at {gadget_file}")
        except Exception as e:
            print_error(f"Error checking gadgets: {e}")

def check_launchers():
    """Check if launcher scripts are installed."""
    print_header("LAUNCHER CHECK")
    
    bin_dir = Path.home() / ".local" / "bin"
    
    launchers = ["kosdwm", "kosdwm-panel"]
    
    for launcher in launchers:
        launcher_path = bin_dir / launcher
        if launcher_path.exists():
            print_success(f"Found: {launcher} at {launcher_path}")
            # Check if it sets KOSDWM_HOME
            try:
                content = launcher_path.read_text()
                if 'KOSDWM_HOME' in content:
                    print_success(f"  Sets KOSDWM_HOME")
                else:
                    print_warning(f"  Does NOT set KOSDWM_HOME")
            except Exception as e:
                print_error(f"  Error reading: {e}")
        else:
            print_error(f"Missing: {launcher} (should be at {launcher_path})")
            print_info(f"  Run: python install_kosdwm.py --user")

def check_panel_integration(kosdwm_path):
    """Check if panel can load gadgets."""
    print_header("PANEL-GADGET INTEGRATION")
    
    # Check if run.py imports and uses gadgets
    run_py = kosdwm_path / "run.py"
    if run_py.exists():
        try:
            content = run_py.read_text()
            if 'GadgetManager' in content:
                print_success("run.py uses GadgetManager")
            else:
                print_warning("run.py does NOT use GadgetManager")
                print_info("  Gadget buttons may not appear in panel")
            
            if 'get_enabled_gadgets' in content:
                print_success("run.py calls get_enabled_gadgets()")
            else:
                print_warning("run.py does NOT call get_enabled_gadgets()")
                print_info("  This is why gadget buttons don't appear!")
        except Exception as e:
            print_error(f"Error reading run.py: {e}")
    else:
        print_error(f"run.py not found at {run_py}")

def print_recommendations():
    """Print recommendations based on findings."""
    print_header("RECOMMENDATIONS")
    
    print_info("Common issues and fixes:")
    print()
    print(f"{Colors.BOLD}1. Gadget buttons not appearing in panel:{Colors.RESET}")
    print("   The panel needs to be connected to the GadgetManager.")
    print("   Edit run.py to add gadget buttons after creating the panel.")
    print()
    print(f"{Colors.BOLD}2. Gadget import errors:{Colors.RESET}")
    print("   Make sure KOSDWM_HOME is set or kosdwm_path.conf exists.")
    print("   Run the install_kosdwm.py script to create launchers.")
    print()
    print(f"{Colors.BOLD}3. Missing gadgets:{Colors.RESET}")
    print("   Check ~/.config/KosDWM/gadgets.json for enabled gadgets.")
    print("   Ensure .py files exist in ~/.config/KosDWM/gadgets/")
    print()
    print(f"{Colors.BOLD}4. To run KosDWM:{Colors.RESET}")
    print("   Use: kosdwm (if installed)")
    print("   Or:  python run.py (from KosDWM directory)")

def main():
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         KosDWM Diagnostic Tool                         ║")
    print(f"╚══════════════════════════════════════════════════════════╝{Colors.RESET}")
    print(f"  Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all checks
    check_environment()
    found_paths = find_kosdwm_path()
    
    # If we found KosDWM, check it
    kosdwm_path = None
    if found_paths:
        kosdwm_path = found_paths[0][1]  # Use first found path
    
    if kosdwm_path:
        check_installation(kosdwm_path)
        check_gadgets(kosdwm_path)
        check_panel_integration(kosdwm_path)
    
    check_launchers()
    print_recommendations()
    
    print_header("DIAGNOSTIC COMPLETE")
    print()
    if kosdwm_path:
        print_success(f"KosDWM found at: {kosdwm_path}")
    else:
        print_error("KosDWM installation not found!")
    
    return 0 if kosdwm_path else 1

if __name__ == "__main__":
    sys.exit(main())
