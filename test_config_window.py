#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
from gadgets import GadgetManager

gm = GadgetManager()
available = gm.get_available_gadgets()
print('Available gadgets:', available)
print('Total:', len(available))

print()
print('What _create_gadget_checkboxes sees:')
for name in available:
    info = gm.get_gadget_info(name)
    enabled = info['enabled']
    print(f'  {name}: enabled={enabled}')
