"""D-Bus client for communicating with midixer daemon"""

import json
import dbus
from typing import List

from ..common.models import MidiMapping, MidiDevice, PipewireNode
from ..common.dbus_iface import DBUS_SERVICE_NAME, DBUS_OBJECT_PATH, DBUS_INTERFACE_NAME


class DaemonClient:
    """Client for communicating with midixer daemon via D-Bus"""

    def __init__(self):
        """Initialize D-Bus client"""
        self.bus = dbus.SessionBus()
        self.proxy = None
        self.connected = False
        self._connect()

    def _connect(self) -> bool:
        """
        Connect to daemon D-Bus service

        Returns:
            True if connected, False otherwise
        """
        try:
            self.proxy = self.bus.get_object(DBUS_SERVICE_NAME, DBUS_OBJECT_PATH)
            self.connected = True
            return True
        except dbus.exceptions.DBusException as e:
            print(f"Failed to connect to daemon: {e}")
            self.connected = False
            return False

    def is_connected(self) -> bool:
        """Check if connected to daemon"""
        return self.connected

    def get_mappings(self) -> List[MidiMapping]:
        """
        Get all MIDI mappings from daemon

        Returns:
            List of MidiMapping objects
        """
        if not self.connected:
            return []

        try:
            mappings_json = self.proxy.GetMappings(dbus_interface=DBUS_INTERFACE_NAME)
            mappings_data = json.loads(mappings_json)
            return [MidiMapping.from_dict(m) for m in mappings_data]
        except Exception as e:
            print(f"Error getting mappings: {e}")
            return []

    def add_mapping(self, mapping: MidiMapping) -> bool:
        """
        Add a new MIDI mapping

        Args:
            mapping: MidiMapping to add

        Returns:
            True if successful
        """
        if not self.connected:
            return False

        try:
            mapping_json = json.dumps(mapping.to_dict())
            return bool(self.proxy.AddMapping(mapping_json, dbus_interface=DBUS_INTERFACE_NAME))
        except Exception as e:
            print(f"Error adding mapping: {e}")
            return False

    def remove_mapping(self, index: int) -> bool:
        """
        Remove a MIDI mapping

        Args:
            index: Index of mapping to remove

        Returns:
            True if successful
        """
        if not self.connected:
            return False

        try:
            return bool(self.proxy.RemoveMapping(index, dbus_interface=DBUS_INTERFACE_NAME))
        except Exception as e:
            print(f"Error removing mapping: {e}")
            return False

    def get_midi_devices(self) -> List[MidiDevice]:
        """
        Get available MIDI devices from daemon

        Returns:
            List of MidiDevice objects
        """
        if not self.connected:
            return []

        try:
            devices_json = self.proxy.GetMidiDevices(dbus_interface=DBUS_INTERFACE_NAME)
            devices_data = json.loads(devices_json)
            return [MidiDevice(**d) for d in devices_data]
        except Exception as e:
            print(f"Error getting MIDI devices: {e}")
            return []

    def get_pipewire_nodes(self) -> List[PipewireNode]:
        """
        Get Pipewire nodes from daemon

        Returns:
            List of PipewireNode objects
        """
        if not self.connected:
            return []

        try:
            nodes_json = self.proxy.GetPipewireNodes(dbus_interface=DBUS_INTERFACE_NAME)
            nodes_data = json.loads(nodes_json)
            return [PipewireNode(**n) for n in nodes_data]
        except Exception as e:
            print(f"Error getting Pipewire nodes: {e}")
            return []

    def reload(self) -> bool:
        """
        Reload daemon configuration

        Returns:
            True if successful
        """
        if not self.connected:
            return False

        try:
            return bool(self.proxy.Reload(dbus_interface=DBUS_INTERFACE_NAME))
        except Exception as e:
            print(f"Error reloading daemon: {e}")
            return False

    def quit_daemon(self) -> None:
        """Tell daemon to quit"""
        if self.connected:
            try:
                self.proxy.Quit(dbus_interface=DBUS_INTERFACE_NAME)
            except Exception as e:
                print(f"Error quitting daemon: {e}")
