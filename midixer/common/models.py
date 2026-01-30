"""Data models for MIDI to Pipewire mappings"""

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class MidiMapping:
    """Represents a mapping between MIDI control and Pipewire node"""

    midi_device: str
    midi_channel: int
    midi_control: int
    pipewire_node_id: int
    pipewire_node_name: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MidiMapping":
        """Create from dictionary"""
        return cls(**data)


@dataclass
class MidiDevice:
    """Represents a MIDI input device"""

    name: str
    port: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)


@dataclass
class PipewireNode:
    """Represents a Pipewire audio node"""

    node_id: int
    name: str
    description: str
    media_class: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)
