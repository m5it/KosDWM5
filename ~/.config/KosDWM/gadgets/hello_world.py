"""
KosDWM Gadget Example - Hello World
====================================

This is an example gadget script for KosDWM.
Place this file in ~/.config/KosDWM/gadgets/ and it will be automatically discovered.

To create your own gadget:
1. Copy this file and rename it (e.g., my_gadget.py)
2. Change the class name and implement the required methods
3. Restart KosDWM or click "Reload Gadgets" in the gadget configuration window
"""

# Required import - GadgetBase is the abstract base class all gadgets must extend
import sys
from pathlib import Path

# Add parent directory to path to import GadgetBase
# This allows the script to find src.gadgets when loaded dynamically
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from gadgets import GadgetBase
from tkinter import messagebox


class HelloWorldGadget(GadgetBase):
    """
    A simple example gadget that shows a greeting message when clicked.
    
    All gadgets must extend GadgetBase and implement the following methods:
    - get_name(): Returns a unique identifier for the gadget
    - get_icon(): Returns the text/icon to display on the button
    - get_tooltip(): Returns tooltip text shown on hover
    - on_click(): Called when the gadget button is clicked
    """
    
    def __init__(self):
        """
        Optional: Custom initialization.
        You can add any setup code here (load settings, initialize state, etc.)
        """
        super().__init__()
        # Example: You could load custom settings here
        self.click_count = 0
    
    def get_name(self) -> str:
        """
        Return the unique name/identifier of this gadget.
        
        This name is used:
        - In the configuration file to track enabled/disabled state
        - As a key in the gadget manager
        
        Must be unique across all gadgets!
        """
        return "hello_world"
    
    def get_icon(self) -> str:
        """
        Return the text/icon to display on the gadget button.
        
        This can be:
        - Text (like "Hello", "CPU", "MEM")
        - Unicode symbols (like "🔋", "📊", "⏰")
        - Short abbreviations (like "HW", "SYS")
        
        Keep it short - 4-6 characters recommended for best appearance.
        """
        return "Hello"
    
    def get_tooltip(self) -> str:
        """
        Return the tooltip text shown when hovering over the gadget.
        
        This should briefly describe what the gadget does.
        """
        return "Click to see Hello World message"
    
    def get_description(self) -> str:
        """
        Optional: Return a longer description for the configuration dialog.
        
        If not implemented, defaults to get_tooltip().
        """
        return "A simple example gadget that shows a greeting message and click counter."
    
    def on_click(self, event=None):
        """
        Handle click events on the gadget button.
        
        This is called when the user clicks the gadget in the panel.
        You can perform any action here:
        - Show a dialog/message
        - Launch an application
        - Toggle a setting
        - Update system state
        
        Args:
            event: The tkinter event object (can be ignored in most cases)
        """
        self.click_count += 1
        messagebox.showinfo(
            "Hello World", 
            f"Hello from KosDWM Gadget!\n\nYou've clicked this gadget {self.click_count} time(s)."
        )


# Optional: You can define multiple gadgets in one file
# class AnotherGadget(GadgetBase):
#     def get_name(self) -> str:
#         return "another_gadget"
#     
#     def get_icon(self) -> str:
#         return "Another"
#     
#     def get_tooltip(self) -> str:
#         return "Another example gadget"
#     
#     def on_click(self, event=None):
#         messagebox.showinfo("Another", "This is another gadget!")


"""
NOTES FOR GADGET DEVELOPERS:
============================

1. File Location:
   - Place your .py file in ~/.config/KosDWM/gadgets/
   - Files starting with _ are ignored

2. Imports:
   - You can import standard library modules freely
   - For external packages, ensure they're installed system-wide
   - To import from KosDWM's src directory, use the path manipulation shown above

3. Multiple Gadgets:
   - You can define multiple gadget classes in a single file
   - Each will be discovered and registered separately

4. State Persistence:
   - If you need to save settings, save them to a file in ~/.config/KosDWM/
   - The gadget instance is recreated each time the panel refreshes

5. Error Handling:
   - Wrap your on_click code in try-except blocks to prevent crashes
   - Errors are logged to stdout/stderr

6. UI Guidelines:
   - Keep icons short (4-6 chars)
   - Tooltips should be concise
   - Avoid blocking operations in on_click (use threading if needed)

7. Testing:
   - After placing your file, click the ⚙ button in the panel
   - Click "Reload Gadgets" to discover your new gadget
   - Enable it and it should appear in the panel

Happy gadget development!
"""
