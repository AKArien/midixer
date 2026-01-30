"""Mapping list widget for displaying and managing MIDI mappings"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from typing import List, Callable
from ..common.models import MidiMapping


class MappingListWidget(Gtk.Box):
    """Widget for displaying and managing MIDI mappings"""
    
    def __init__(self, on_remove_callback: Callable[[int], None]):
        """
        Initialize mapping list widget
        
        Args:
            on_remove_callback: Callback when remove button is clicked
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        self.on_remove_callback = on_remove_callback
        
        # Create scrolled window for list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(200)
        
        # Create list box
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(self.listbox)
        
        # Add label
        label = Gtk.Label(label="Active Mappings")
        label.set_halign(Gtk.Align.START)
        label.get_style_context().add_class("heading")
        
        self.pack_start(label, False, False, 0)
        self.pack_start(scrolled, True, True, 0)
    
    def update_mappings(self, mappings: List[MidiMapping]) -> None:
        """
        Update the list of mappings
        
        Args:
            mappings: List of MidiMapping objects
        """
        # Clear existing items
        for child in self.listbox.get_children():
            self.listbox.remove(child)
        
        # Add new items
        for i, mapping in enumerate(mappings):
            row = self._create_mapping_row(i, mapping)
            self.listbox.add(row)
        
        self.listbox.show_all()
    
    def _create_mapping_row(self, index: int, mapping: MidiMapping) -> Gtk.ListBoxRow:
        """
        Create a row for a mapping
        
        Args:
            index: Index of the mapping
            mapping: MidiMapping object
            
        Returns:
            Gtk.ListBoxRow
        """
        row = Gtk.ListBoxRow()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_margin_top(6)
        box.set_margin_bottom(6)
        box.set_margin_start(6)
        box.set_margin_end(6)
        
        # Mapping info
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        
        title = Gtk.Label(label=f"<b>{mapping.pipewire_node_name}</b>")
        title.set_use_markup(True)
        title.set_halign(Gtk.Align.START)
        
        details = Gtk.Label(
            label=f"MIDI Channel {mapping.midi_channel}, "
                  f"Control {mapping.midi_control} → Node {mapping.pipewire_node_id}"
        )
        details.set_halign(Gtk.Align.START)
        details.get_style_context().add_class("dim-label")
        
        info_box.pack_start(title, False, False, 0)
        info_box.pack_start(details, False, False, 0)
        
        box.pack_start(info_box, True, True, 0)
        
        # Remove button
        remove_button = Gtk.Button(label="Remove")
        remove_button.get_style_context().add_class("destructive-action")
        remove_button.connect("clicked", lambda btn: self.on_remove_callback(index))
        
        box.pack_end(remove_button, False, False, 0)
        
        row.add(box)
        return row
