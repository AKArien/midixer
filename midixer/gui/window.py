"""Main GTK window for midixer GUI"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

from typing import Optional
from ..common.models import MidiMapping, MidiDevice, PipewireNode
from .dbus_client import DaemonClient
from .mapping_list import MappingListWidget


class MidixerWindow(Gtk.Window):
    """Main window for midixer configuration"""
    
    def __init__(self):
        """Initialize the window"""
        super().__init__(title="Midixer - MIDI Volume Controller")
        
        self.set_default_size(700, 500)
        self.set_border_width(10)
        
        # Initialize daemon client
        self.client = DaemonClient()
        
        # State
        self.midi_devices = []
        self.pipewire_nodes = []
        self.mappings = []
        
        # Build UI
        self._build_ui()
        
        # Load initial data
        self._refresh_data()
        
        # Setup periodic refresh
        GLib.timeout_add_seconds(5, self._refresh_data)
    
    def _build_ui(self) -> None:
        """Build the user interface"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Connection status
        self.status_label = Gtk.Label()
        self.status_label.set_halign(Gtk.Align.START)
        main_box.pack_start(self.status_label, False, False, 0)
        
        # Create mapping section
        create_frame = Gtk.Frame(label="Create New Mapping")
        create_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        create_box.set_margin_top(12)
        create_box.set_margin_bottom(12)
        create_box.set_margin_start(12)
        create_box.set_margin_end(12)
        
        # MIDI device dropdown
        midi_label = Gtk.Label(label="MIDI Device:")
        midi_label.set_halign(Gtk.Align.START)
        self.midi_combo = Gtk.ComboBoxText()
        create_box.pack_start(midi_label, False, False, 0)
        create_box.pack_start(self.midi_combo, False, False, 0)
        
        # MIDI channel input
        channel_label = Gtk.Label(label="MIDI Channel (0-15):")
        channel_label.set_halign(Gtk.Align.START)
        self.channel_spin = Gtk.SpinButton()
        self.channel_spin.set_range(0, 15)
        self.channel_spin.set_increments(1, 1)
        self.channel_spin.set_value(0)
        create_box.pack_start(channel_label, False, False, 0)
        create_box.pack_start(self.channel_spin, False, False, 0)
        
        # MIDI control input
        control_label = Gtk.Label(label="MIDI Control (0-127):")
        control_label.set_halign(Gtk.Align.START)
        self.control_spin = Gtk.SpinButton()
        self.control_spin.set_range(0, 127)
        self.control_spin.set_increments(1, 10)
        self.control_spin.set_value(1)
        create_box.pack_start(control_label, False, False, 0)
        create_box.pack_start(self.control_spin, False, False, 0)
        
        # Pipewire node dropdown
        node_label = Gtk.Label(label="Pipewire Node:")
        node_label.set_halign(Gtk.Align.START)
        self.node_combo = Gtk.ComboBoxText()
        create_box.pack_start(node_label, False, False, 0)
        create_box.pack_start(self.node_combo, False, False, 0)
        
        # Add button
        add_button = Gtk.Button(label="Add Mapping")
        add_button.get_style_context().add_class("suggested-action")
        add_button.connect("clicked", self._on_add_mapping)
        create_box.pack_start(add_button, False, False, 6)
        
        create_frame.add(create_box)
        main_box.pack_start(create_frame, False, False, 0)
        
        # Mappings list
        self.mapping_list = MappingListWidget(self._on_remove_mapping)
        main_box.pack_start(self.mapping_list, True, True, 0)
        
        # Bottom buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        refresh_button = Gtk.Button(label="Refresh")
        refresh_button.connect("clicked", lambda btn: self._refresh_data())
        button_box.pack_start(refresh_button, False, False, 0)
        
        main_box.pack_start(button_box, False, False, 0)
        
        self.add(main_box)
    
    def _refresh_data(self) -> bool:
        """
        Refresh data from daemon
        
        Returns:
            True to continue periodic refresh
        """
        # Update connection status
        if self.client.is_connected():
            self.status_label.set_markup("<b>Status:</b> Connected to daemon")
        else:
            self.status_label.set_markup(
                "<b>Status:</b> <span color='red'>Not connected to daemon</span>"
            )
            return True
        
        # Get MIDI devices
        self.midi_devices = self.client.get_midi_devices()
        self.midi_combo.remove_all()
        for device in self.midi_devices:
            self.midi_combo.append_text(device.name)
        if self.midi_devices:
            self.midi_combo.set_active(0)
        
        # Get Pipewire nodes
        self.pipewire_nodes = self.client.get_pipewire_nodes()
        self.node_combo.remove_all()
        for node in self.pipewire_nodes:
            display_text = f"{node.name} (ID: {node.node_id})"
            self.node_combo.append_text(display_text)
        if self.pipewire_nodes:
            self.node_combo.set_active(0)
        
        # Get mappings
        self.mappings = self.client.get_mappings()
        self.mapping_list.update_mappings(self.mappings)
        
        return True
    
    def _on_add_mapping(self, button: Gtk.Button) -> None:
        """Handle add mapping button click"""
        # Get selected values
        midi_idx = self.midi_combo.get_active()
        node_idx = self.node_combo.get_active()
        
        if midi_idx < 0 or node_idx < 0:
            self._show_error("Please select both MIDI device and Pipewire node")
            return
        
        midi_device = self.midi_devices[midi_idx]
        node = self.pipewire_nodes[node_idx]
        
        channel = int(self.channel_spin.get_value())
        control = int(self.control_spin.get_value())
        
        # Create mapping
        mapping = MidiMapping(
            midi_device=midi_device.name,
            midi_channel=channel,
            midi_control=control,
            pipewire_node_id=node.node_id,
            pipewire_node_name=node.name
        )
        
        # Add to daemon
        if self.client.add_mapping(mapping):
            self._refresh_data()
        else:
            self._show_error("Failed to add mapping")
    
    def _on_remove_mapping(self, index: int) -> None:
        """Handle remove mapping request"""
        if self.client.remove_mapping(index):
            self._refresh_data()
        else:
            self._show_error("Failed to remove mapping")
    
    def _show_error(self, message: str) -> None:
        """Show error dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()
