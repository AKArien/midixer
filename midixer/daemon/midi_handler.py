"""MIDI event handler for midixer daemon"""

import rtmidi
from typing import Callable, List, Optional
from ..common.models import MidiDevice


class MidiHandler:
    """Handles MIDI input events"""

    def __init__(self):
        """Initialize MIDI handler"""
        self.midi_in = rtmidi.MidiIn()
        self.callback: Optional[Callable] = None
        self.current_port: Optional[int] = None

    def get_available_devices(self) -> List[MidiDevice]:
        """Get list of available MIDI input devices"""
        devices = []
        port_count = self.midi_in.get_port_count()

        for i in range(port_count):
            port_name = self.midi_in.get_port_name(i)
            devices.append(MidiDevice(name=port_name, port=i))

        return devices

    def open_port(self, port: int) -> bool:
        """
        Open a MIDI input port

        Args:
            port: Port number to open

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.current_port is not None:
                self.close_port()

            self.midi_in.open_port(port)
            self.current_port = port
            self.midi_in.set_callback(self._midi_callback)
            return True
        except Exception as e:
            print(f"Error opening MIDI port {port}: {e}")
            return False

    def close_port(self) -> None:
        """Close the current MIDI input port"""
        if self.current_port is not None:
            self.midi_in.close_port()
            self.current_port = None

    def set_callback(self, callback: Callable) -> None:
        """
        Set callback function for MIDI events

        Args:
            callback: Function to call with (channel, control, value) arguments
        """
        self.callback = callback

    def _midi_callback(self, event, data=None) -> None:
        """
        Internal callback for MIDI events

        Args:
            event: MIDI event data (message, timestamp)
        """
        message, timestamp = event

        if len(message) < 3:
            return

        # Parse MIDI Control Change message (0xB0 = CC on channel 0)
        status = message[0]
        if (status & 0xF0) == 0xB0:  # Control Change
            channel = status & 0x0F
            control = message[1]
            value = message[2]

            if self.callback:
                self.callback(channel, control, value)

    def __del__(self):
        """Cleanup on deletion"""
        self.close_port()
