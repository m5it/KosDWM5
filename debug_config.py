#!/usr/bin/env python3
import sys
import tkinter as tk
sys.path.insert(0, 'src')
from gadgets import GadgetManager, GadgetConfigWindow

# Create a test window
root = tk.Tk()
root.withdraw()

gm = GadgetManager()
print("Available gadgets:", gm.get_available_gadgets())
print("Enabled:", [g.get_name() for g in gm.get_enabled_gadgets()])

# Create config window
def on_save():
    print("Save clicked!")
    print("Enabled after save:", [g.get_name() for g in gm.get_enabled_gadgets()])

config = GadgetConfigWindow(root, gm, on_save_callback=on_save)

# Print what checkboxes were created
print("Checkboxes created:", list(config.checkboxes.keys()))

root.mainloop()
