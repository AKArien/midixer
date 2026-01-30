# Midixer

**MIDI Volume Controller for Pipewire**

Midixer is a daemon and GUI application that allows you to control Pipewire audio volumes using MIDI controllers. Map MIDI channels/controls to specific Pipewire nodes and adjust volumes in real-time.

## Features

- 🎛️ **MIDI Integration**: Use any MIDI controller to control system volumes
- 🎵 **Pipewire Native**: Built specifically for Pipewire/Wireplumber
- 🖥️ **GTK GUI**: Easy-to-use graphical interface for configuration
- 🔄 **Real-time Configuration**: Change mappings on the fly without restarting
- 💾 **Persistent Mappings**: Save your MIDI-to-node configurations
- 🔌 **D-Bus Communication**: Efficient daemon-GUI communication

## Architecture

Midixer consists of two main components:

### Daemon (`midixer-daemon`)
- Listens for MIDI events from connected controllers
- Applies volume changes to Pipewire nodes via Wireplumber
- Exposes a D-Bus interface for runtime configuration
- Runs in the background as a user service

### GUI (`midixer-gui`)
- GTK-based configuration interface
- Shows available MIDI controllers and Pipewire nodes
- Allows creating/editing/deleting MIDI-to-node mappings
- Communicates with daemon via D-Bus

## Installation

### Requirements

- Python 3.9 or higher
- Pipewire (with Wireplumber)
- GTK 3.0+
- ALSA MIDI support

### From Source

```bash
# Clone the repository
git clone https://github.com/AKArien/midixer.git
cd midixer

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# For development
pip install -e ".[dev]"
```

### System-wide Installation

```bash
pip install .
```

## Usage

### Starting the Daemon

```bash
# Run in foreground
midixer-daemon

# Run in background with systemd (recommended)
# Copy service file
mkdir -p ~/.config/systemd/user/
cp systemd/midixer-daemon.service ~/.config/systemd/user/

# Enable and start service
systemctl --user daemon-reload
systemctl --user enable midixer-daemon
systemctl --user start midixer-daemon

# Check status
systemctl --user status midixer-daemon
```

### Using the GUI

```bash
midixer-gui
```

### Configuration Workflow

1. Start the daemon: `midixer-daemon`
2. Launch the GUI: `midixer-gui`
3. In the GUI:
   - Select a MIDI controller from the dropdown
   - Select a MIDI channel/control
   - Select a Pipewire node (application/device)
   - Click "Add Mapping"
4. Move the MIDI control to test the volume change
5. Mappings are saved automatically

## Configuration File

Mappings are stored in `~/.config/midixer/config.json`:

```json
{
  "mappings": [
    {
      "midi_device": "Akai MPK Mini",
      "midi_channel": 0,
      "midi_control": 1,
      "pipewire_node_id": 42,
      "pipewire_node_name": "Firefox"
    }
  ]
}
```

## Development

### Project Structure

```
midixer/
├── midixer/
│   ├── common/          # Shared code (config, IPC, models)
│   │   ├── __init__.py
│   │   ├── config.py    # Configuration management
│   │   ├── dbus_iface.py # D-Bus interface definitions
│   │   └── models.py    # Data models
│   ├── daemon/          # Daemon implementation
│   │   ├── __init__.py
│   │   ├── main.py      # Entry point
│   │   ├── midi_handler.py # MIDI event handling
│   │   ├── pipewire_controller.py # Pipewire/Wireplumber integration
│   │   └── dbus_server.py # D-Bus service
│   └── gui/             # GUI implementation
│       ├── __init__.py
│       ├── main.py      # Entry point
│       ├── window.py    # Main window
│       ├── mapping_list.py # Mapping management UI
│       └── dbus_client.py # D-Bus client
├── tests/               # Unit tests
│   ├── daemon/
│   ├── gui/
│   └── common/
├── pyproject.toml       # Project configuration
├── README.md
└── .github/
    └── workflows/
        └── ci.yml       # CI/CD pipeline
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=midixer

# Run specific test file
pytest tests/daemon/test_midi_handler.py
```

### Code Style

```bash
# Format code
black midixer/

# Lint code
flake8 midixer/

# Type checking
mypy midixer/
```

## Troubleshooting

### Daemon won't start
- Ensure Pipewire is running: `systemctl --user status pipewire`
- Check MIDI devices are available: `aconnect -l`

### GUI can't connect to daemon
- Verify daemon is running: `ps aux | grep midixer-daemon`
- Check D-Bus service: `busctl --user status org.midixer.Daemon`

### MIDI events not working
- Test MIDI input: `aseqdump -p <port>`
- Check daemon logs: `journalctl --user -u midixer-daemon`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built with [python-rtmidi](https://pypi.org/project/python-rtmidi/)
- Pipewire integration via [pywireplumber](https://gitlab.freedesktop.org/pipewire/wireplumber)
- GUI built with [GTK](https://www.gtk.org/) and [PyGObject](https://pygobject.readthedocs.io/)
