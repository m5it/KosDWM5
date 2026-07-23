#!/usr/bin/env python3
"""Create auto-versioning files for KosDWM"""

import os

# AUTOVERSION.py content
autoversion_content = '''#!/usr/bin/env python3
# Auto-generated version file - do not edit manually
# Incremented automatically by git pre-commit hook

VERSION = "1.0.0"

if __name__ == "__main__":
    import sys
    if "-c" in sys.argv or "--current" in sys.argv:
        print(VERSION)
    elif "-h" in sys.argv or "--help" in sys.argv:
        print("Usage: python AUTOVERSION.py [-c|--current] [-h|--help]")
        print("  -c, --current  Print current version")
        print("  -h, --help     Show this help")
    else:
        print(f"KosDWM Auto-Version: {VERSION}")
'''

# CHANGELOG.md content
changelog_content = '''# Changelog

All notable changes to KosDWM will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial auto-versioning system

## [1.0.0] - 2025-01-21

### Added
- Initial release of KosDWM
- Dynamic window management
- Python-based gadget system
- Panel with customizable gadgets
- HTTP API for notices
- Notification system with reminders
'''

# install_hooks.py content
install_hooks_content = '''#!/usr/bin/env python3
"""
Install Git Hooks for KosDWM Auto-Versioning
"""

import os
import sys
import stat
from pathlib import Path


HOOK_CONTENT = """#!/usr/bin/env python3
\\"\\"\\"Pre-commit hook: auto-increment version in AUTOVERSION.py + update CHANGELOG.md\\"\\"\\"
import re
import sys
import subprocess
import os
from datetime import date

REPO_ROOT = subprocess.run(
    ['git', 'rev-parse', '--show-toplevel'],
    capture_output=True, text=True
).stdout.strip()

VERSION_FILE = os.path.join(REPO_ROOT, 'AUTOVERSION.py')
CHANGELOG_FILE = os.path.join(REPO_ROOT, 'CHANGELOG.md')

# Skip on merge commits
merge_msg = os.path.join(REPO_ROOT, '.git', 'MERGE_MSG')
if os.path.exists(merge_msg):
    with open(merge_msg) as f:
        if 'Merge' in f.read():
            sys.exit(0)

if not os.path.exists(VERSION_FILE):
    sys.exit(0)

with open(VERSION_FILE) as f:
    content = f.read()

match = re.search(r'VERSION\\\\s*=\\\\s*\"([^\"]+)\"', content)
if not match:
    sys.exit(0)

current = match.group(1)
parts = current.split('.')

if len(parts) == 3:
    new = \"{}.{}.{}\".format(parts[0], parts[1], int(parts[2]) + 1)
elif len(parts) == 2:
    new = \"{}.{}.1\".format(parts[0], parts[1])
else:
    sys.exit(0)

result = subprocess.run(
    ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACDMR'],
    capture_output=True, text=True
)
changed_files = [f for f in result.stdout.strip().split('\\\\n') if f]

content = content.replace('VERSION = \"{}\"'.format(current), 'VERSION = \"{}\"'.format(new))
with open(VERSION_FILE, 'w') as f:
    f.write(content)

print(f\"Version: {current} -> {new}\")

today = date.today().isoformat()
files_str = ', '.join(changed_files[:5])
if len(changed_files) > 5:
    files_str += f\" +{len(changed_files) - 5}\"

new_entry = f\"\"\"## [{new}] - {today}

### Changed
- Auto-incremented from {current}
- Files: {files_str}

\"\"\"

if os.path.exists(CHANGELOG_FILE):
    with open(CHANGELOG_FILE) as f:
        old_changelog = f.read()
else:
    old_changelog = \"# Changelog\\\\n\\\\n\"

lines = old_changelog.split('\\\\n')
new_lines = []
header_done = False

for line in lines:
    if not header_done and line.startswith('#'):
        new_lines.append(line)
        if 'Changelog' in line:
            header_done = True
            new_lines.append(\"\")
            new_lines.append(new_entry.strip())
            new_lines.append(\"\")
    else:
        new_lines.append(line)

with open(CHANGELOG_FILE, 'w') as f:
    f.write('\\\\n'.join(new_lines))

subprocess.run(['git', 'add', VERSION_FILE, CHANGELOG_FILE])
"""


def install_hooks():
    \"\"\"Install git hooks.\"\"\"
    repo_root = Path(__file__).parent.resolve()
    git_dir = repo_root / \".git\"
    
    if not git_dir.exists():
        print(\"Error: Not a git repository\")
        return 1
    
    hooks_dir = git_dir / \"hooks\"
    hooks_dir.mkdir(exist_ok=True)
    
    pre_commit = hooks_dir / \"pre-commit\"
    pre_commit.write_text(HOOK_CONTENT)
    pre_commit.chmod(pre_commit.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    
    print(f\"✓ Installed pre-commit hook: {pre_commit}\")
    print()
    print(\"Auto-versioning active!\")
    print(\"Every commit will:\")
    print(\"  1. Increment version in AUTOVERSION.py\")
    print(\"  2. Update CHANGELOG.md\")
    print()
    print(\"Check version: python AUTOVERSION.py\")
    
    return 0


if __name__ == \"__main__\":
    sys.exit(install_hooks())
'''


def main():
    # Create files
    files = {
        'AUTOVERSION.py': autoversion_content,
        'CHANGELOG.md': changelog_content,
        'install_hooks.py': install_hooks_content,
    }
    
    for filename, content in files.items():
        with open(filename, 'w') as f:
            f.write(content)
        print(f"Created: {filename}")
    
    # Make install_hooks.py executable
    os.chmod('install_hooks.py', 0o755)
    print("Made install_hooks.py executable")
    print()
    print("Next steps:")
    print("  1. python install_hooks.py")
    print("  2. git add AUTOVERSION.py CHANGELOG.md")
    print("  3. git commit -m 'Add auto-versioning'")


if __name__ == "__main__":
    main()
