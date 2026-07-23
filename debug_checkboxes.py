#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
from gadgets import GadgetManager

gm = GadgetManager()
print('=== DEBUG ===')
print('Available:', gm.get_available_gadgets())
print('Enabled:', [g.get_name() for g in gm.get_enabled_gadgets()])

# Check what _create_gadget_checkboxes would see
available = gm.get_available_gadgets()
print('Total available:', len(available))
for name in available:
    info = gm.get_gadget_info(name)
    enabled = info['enabled']
    print(f'  {name}: enabled={enabled}')
