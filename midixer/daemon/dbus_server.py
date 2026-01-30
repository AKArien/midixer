"""D-Bus server for midixer daemon"""

import json
import dbus
import dbus.service
from typing import TYPE_CHECKING

from ..common.dbus_iface import DBUS_SERVICE_NAME, DBUS_OBJECT_PATH, DBUS_INTERFACE_NAME

if TYPE_CHECKING:
    from .main import MidixerDaemon


class DaemonDBusService(dbus.service.Object):
    """D-Bus service for midixer daemon"""

    def __init__(self, daemon: "MidixerDaemon", bus: dbus.Bus):
        """
        Initialize D-Bus service

        Args:
            daemon: Reference to main daemon instance
            bus: D-Bus bus connection
        """
        self.daemon = daemon
        bus_name = dbus.service.BusName(DBUS_SERVICE_NAME, bus=bus)
        super().__init__(bus_name, DBUS_OBJECT_PATH)

    @dbus.service.method(DBUS_INTERFACE_NAME, out_signature="s")
    def GetMappings(self) -> str:
        """Get all MIDI mappings as JSON string"""
        mappings = self.daemon.config.get_mappings()
        mappings_dict = [m.to_dict() for m in mappings]
        return json.dumps(mappings_dict)

    @dbus.service.method(DBUS_INTERFACE_NAME, in_signature="s", out_signature="b")
    def AddMapping(self, mapping_json: str) -> bool:
        """
        Add a new MIDI mapping

        Args:
            mapping_json: JSON string representing the mapping

        Returns:
            True if successful
        """
        try:
            from ..common.models import MidiMapping

            mapping_dict = json.loads(mapping_json)
            mapping = MidiMapping.from_dict(mapping_dict)
            self.daemon.add_mapping(mapping)
            self.MappingChanged("added")
            return True
        except Exception as e:
            print(f"Error adding mapping: {e}")
            return False

    @dbus.service.method(DBUS_INTERFACE_NAME, in_signature="i", out_signature="b")
    def RemoveMapping(self, index: int) -> bool:
        """
        Remove a MIDI mapping by index

        Args:
            index: Index of mapping to remove

        Returns:
            True if successful
        """
        try:
            self.daemon.remove_mapping(index)
            self.MappingChanged("removed")
            return True
        except Exception as e:
            print(f"Error removing mapping: {e}")
            return False

    @dbus.service.method(DBUS_INTERFACE_NAME, out_signature="s")
    def GetMidiDevices(self) -> str:
        """Get available MIDI devices as JSON string"""
        devices = self.daemon.midi_handler.get_available_devices()
        devices_dict = [d.to_dict() for d in devices]
        return json.dumps(devices_dict)

    @dbus.service.method(DBUS_INTERFACE_NAME, out_signature="s")
    def GetPipewireNodes(self) -> str:
        """Get Pipewire nodes as JSON string"""
        nodes = self.daemon.pipewire_controller.get_nodes()
        nodes_dict = [n.to_dict() for n in nodes]
        return json.dumps(nodes_dict)

    @dbus.service.method(DBUS_INTERFACE_NAME, out_signature="b")
    def Reload(self) -> bool:
        """
        Reload configuration

        Returns:
            True if successful
        """
        try:
            self.daemon.reload_config()
            return True
        except Exception as e:
            print(f"Error reloading config: {e}")
            return False

    @dbus.service.method(DBUS_INTERFACE_NAME)
    def Quit(self):
        """Quit the daemon"""
        self.daemon.quit()

    @dbus.service.signal(DBUS_INTERFACE_NAME, signature="s")
    def MappingChanged(self, action: str):
        """
        Signal emitted when mappings change

        Args:
            action: Type of change (added, removed, etc.)
        """
        pass
