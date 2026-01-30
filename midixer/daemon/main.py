"""Main entry point for midixer daemon"""

import sys
import signal
from typing import Dict, Tuple
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

from ..common.config import Config
from ..common.models import MidiMapping
from .midi_handler import MidiHandler
from .pipewire_controller import PipewireController
from .dbus_server import DaemonDBusService


class MidixerDaemon:
    """Main daemon class for midixer"""
    
    def __init__(self):
        """Initialize the daemon"""
        print("Initializing midixer daemon...")
        
        # Initialize components
        self.config = Config()
        self.midi_handler = MidiHandler()
        self.pipewire_controller = PipewireController()
        
        # Mapping cache: (channel, control) -> node_id
        self.active_mappings: Dict[Tuple[int, int], int] = {}
        
        # D-Bus setup
        DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SessionBus()
        self.dbus_service = DaemonDBusService(self, self.bus)
        
        # GLib main loop
        self.mainloop = GLib.MainLoop()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Load configuration and setup MIDI
        self.reload_config()
        
        print("Midixer daemon initialized")
    
    def _signal_handler(self, signum, frame):
        """Handle termination signals"""
        print(f"\nReceived signal {signum}, shutting down...")
        self.quit()
    
    def reload_config(self) -> None:
        """Reload configuration and update active mappings"""
        print("Loading configuration...")
        self.config.load()
        
        # Rebuild mapping cache
        self.active_mappings.clear()
        for mapping in self.config.get_mappings():
            key = (mapping.midi_channel, mapping.midi_control)
            self.active_mappings[key] = mapping.pipewire_node_id
        
        print(f"Loaded {len(self.active_mappings)} mappings")
        
        # Setup MIDI handler if we have mappings
        if self.active_mappings:
            devices = self.midi_handler.get_available_devices()
            if devices:
                print(f"Found {len(devices)} MIDI devices")
                # Open first available device for now
                if self.midi_handler.open_port(0):
                    print(f"Opened MIDI port 0: {devices[0].name}")
                    self.midi_handler.set_callback(self._on_midi_event)
            else:
                print("No MIDI devices found")
    
    def _on_midi_event(self, channel: int, control: int, value: int) -> None:
        """
        Handle incoming MIDI events
        
        Args:
            channel: MIDI channel (0-15)
            control: MIDI control number (0-127)
            value: MIDI control value (0-127)
        """
        # Check if this control is mapped
        key = (channel, control)
        if key in self.active_mappings:
            node_id = self.active_mappings[key]
            
            # Convert MIDI value (0-127) to volume (0.0-1.0)
            volume = value / 127.0
            
            # Apply volume change
            if self.pipewire_controller.set_volume(node_id, volume):
                print(f"Set node {node_id} volume to {volume:.2f}")
            else:
                print(f"Failed to set volume for node {node_id}")
    
    def add_mapping(self, mapping: MidiMapping) -> None:
        """Add a new mapping"""
        self.config.add_mapping(mapping)
        key = (mapping.midi_channel, mapping.midi_control)
        self.active_mappings[key] = mapping.pipewire_node_id
        print(f"Added mapping: channel {mapping.midi_channel}, "
              f"control {mapping.midi_control} -> node {mapping.pipewire_node_id}")
    
    def remove_mapping(self, index: int) -> None:
        """Remove a mapping by index"""
        mappings = self.config.get_mappings()
        if 0 <= index < len(mappings):
            mapping = mappings[index]
            key = (mapping.midi_channel, mapping.midi_control)
            if key in self.active_mappings:
                del self.active_mappings[key]
            self.config.remove_mapping(index)
            print(f"Removed mapping at index {index}")
    
    def run(self) -> None:
        """Run the daemon main loop"""
        print("Starting midixer daemon...")
        print("Press Ctrl+C to quit")
        try:
            self.mainloop.run()
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        finally:
            self.cleanup()
    
    def quit(self) -> None:
        """Quit the daemon"""
        self.mainloop.quit()
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        print("Cleaning up...")
        self.midi_handler.close_port()


def main():
    """Main entry point"""
    daemon = MidixerDaemon()
    daemon.run()
    return 0


if __name__ == '__main__':
    sys.exit(main())
