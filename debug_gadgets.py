#!/usr/bin/env python3
import sys
import json
import os

print('=== Environment Check ===')
print('Python path:', sys.path[:3])
print('CWD:', os.getcwd())
print('HOME:', os.environ.get('HOME'))

print()
print('=== Gadgets.json Content ===')
config_path = os.path.expanduser('~/.config/KosDWM/gadgets.json')
if os.path.exists(config_path):
    with open(config_path) as f:
        config = json.load(f)
    print('Config:', json.dumps(config, indent=2))
else:
    print('File not found:', config_path)

print()
print('=== Gadget Files ===')
gadgets_dir = os.path.expanduser('~/.config/KosDWM/gadgets/')
if os.path.exists(gadgets_dir):
    files = [f for f in os.listdir(gadgets_dir) if f.endswith('.py') and not f.startswith('_')]
    print('Files:', files)
else:
    print('Dir not found:', gadgets_dir)

print()
print('=== Loading GadgetManager ===')
sys.path.insert(0, 'src')
from gadgets import GadgetManager

gm = GadgetManager()
print('Available gadgets:', gm.get_available_gadgets())
print('Enabled gadgets:', [g.get_name() for g in gm.get_enabled_gadgets()])
print('Load errors:', gm.get_load_errors())

print()
print('=== Detailed Gadget Info ===')
for name in gm.get_available_gadgets():
    info = gm.get_gadget_info(name)
    print(f'{name}:')
    print(f'  enabled: {info["enabled"]}')
    print(f'  source: {info["source"]}')
    print(f'  icon: {info["icon"]}')

print()
print('=== Checking for duplicate configs ===')
for root, dirs, files in os.walk(os.path.expanduser('~/.config')):
    if 'gadgets.json' in files:
        full_path = os.path.join(root, 'gadgets.json')
        print(f'Found: {full_path}')
        try:
            with open(full_path) as f:
                print(f'  Content: {json.dumps(json.load(f), indent=2)}')
        except Exception as e:
            print(f'  Error reading: {e}')
