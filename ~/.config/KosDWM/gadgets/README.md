# KosDWM Gadgets

This directory contains custom gadgets for the KosDWM panel. Gadgets are small Python scripts that add interactive elements to your panel.

## Quick Start

1. Create a new file with a `.py` extension in this directory
2. Define a class that extends `GadgetBase`
3. Implement the required methods
4. Click the ⚙ (gear) button in the panel and select "Reload Gadgets"
5. Enable your new gadget in the configuration window

## Gadget Structure

Every gadget must follow this structure:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from gadgets import GadgetBase


class MyGadget(GadgetBase):
    """Your gadget class description."""
    
    def get_name(self) -> str:
        """Unique identifier for this gadget."""
        return "my_gadget"
    
    def get_icon(self) -> str:
        """Text/icon shown on the button (keep it short!)."""
        return "MY"
    
    def get_tooltip(self) -> str:
        """Text shown when hovering over the gadget."""
        return "Click to activate my gadget"
    
    def on_click(self, event=None):
        """Called when the gadget is clicked."""
        # Your action here
        pass
```

## Required Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `get_name()` | `str` | Unique identifier (used in config) |
| `get_icon()` | `str` | Button label (4-6 chars recommended) |
| `get_tooltip()` | `str` | Hover tooltip text |
| `on_click(event)` | `None` | Click handler |

## Optional Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `get_description()` | `str` | Longer description for config dialog |
| `__init__()` | - | Custom initialization |

## Example Gadgets

### hello_world.py
A simple gadget that shows a greeting message. Good starting point for understanding the basics.

### system_info.py
Displays system information (hostname, OS, uptime, memory). Shows how to run system commands.

### cpu_monitor.py
Monitors CPU usage by reading `/proc/stat`. Demonstrates reading system statistics.

## Tips

- **Icons**: Use short text or Unicode symbols (e.g., "🔋", "📊", "⏰")
- **Keep it fast**: Avoid slow operations in `on_click()` - use threading if needed
- **Error handling**: Wrap code in try-except to prevent crashes
- **Multiple gadgets**: You can define multiple classes in one file
- **Settings**: Save custom settings to `~/.config/KosDWM/` if needed

## Troubleshooting

**Gadget not appearing:**
- Check the file ends with `.py`
- Ensure the class extends `GadgetBase`
- Look for errors in the terminal output
- Click "Reload Gadgets" in the configuration window

**Import errors:**
- Make sure the path insertion code is at the top of your file
- Verify `GadgetBase` is imported correctly

**Gadget crashes:**
- Check that all required methods are implemented
- Add error handling with try-except blocks

## Advanced Features

### Running System Commands
```python
import subprocess

def on_click(self, event=None):
    result = subprocess.run(['date'], capture_output=True, text=True)
    messagebox.showinfo("Date", result.stdout)
```

### Reading Files
```python
def on_click(self, event=None):
    with open('/proc/loadavg', 'r') as f:
        load = f.read().strip()
    messagebox.showinfo("Load", load)
```

### State Persistence
```python
def __init__(self):
    super().__init__()
    self.click_count = 0

def on_click(self, event=None):
    self.click_count += 1
    messagebox.showinfo("Clicks", f"Clicked {self.click_count} times")
```

## File Location

Gadgets are loaded from: `~/.config/KosDWM/gadgets/`

Files starting with `_` are ignored.

## Reloading

After adding or modifying gadgets:
1. Click the ⚙ (gear) button in the panel
2. Click "Reload Gadgets" in the configuration window
3. Your changes should appear immediately

## Sharing Gadgets

To share a gadget with others, simply share the `.py` file. Others can place it in their gadgets directory and it will be automatically discovered.

Happy gadget development!
