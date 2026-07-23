# KosDWM

A dynamic window manager with Python-based gadget system.

## Features

- **Dynamic Window Management** - Tiling window manager for X11
- **Gadget System** - Pluggable Python gadgets for the panel
- **Notices & Reminders** - Built-in notification system with HTTP API
- **Auto-Versioning** - Automatic version increment on commits

## Quick Start

```bash
# Install
python install_kosdwm.py

# Run
kosdwm
```

## Configuration

Create `~/.config/KosDWM/config.json`:

```json
{
    "active_button_bg": "#4a90d9",
    "inactive_button_bg": "#606060",
    "bar_height": 25,
    "layout_mode": "comboboxes"
}
```

## Documentation

- [Notices API](NOTICES_API_DOCUMENTATION.md) - HTTP API for notices
- [Changelog](CHANGELOG.md) - Version history

## License

MIT License - Created with love by B.K. and OpenCode ( editor + BigPickle ) and ollama models.
