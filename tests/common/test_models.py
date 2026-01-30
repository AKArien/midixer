"""Tests for data models"""

from midixer.common.models import MidiMapping, MidiDevice, PipewireNode


def test_midi_mapping_to_dict():
    """Test MidiMapping serialization to dict"""
    mapping = MidiMapping(
        midi_device="Test Device",
        midi_channel=0,
        midi_control=1,
        pipewire_node_id=42,
        pipewire_node_name="Test Node"
    )
    
    data = mapping.to_dict()
    
    assert data['midi_device'] == "Test Device"
    assert data['midi_channel'] == 0
    assert data['midi_control'] == 1
    assert data['pipewire_node_id'] == 42
    assert data['pipewire_node_name'] == "Test Node"


def test_midi_mapping_from_dict():
    """Test MidiMapping deserialization from dict"""
    data = {
        'midi_device': "Test Device",
        'midi_channel': 0,
        'midi_control': 1,
        'pipewire_node_id': 42,
        'pipewire_node_name': "Test Node"
    }
    
    mapping = MidiMapping.from_dict(data)
    
    assert mapping.midi_device == "Test Device"
    assert mapping.midi_channel == 0
    assert mapping.midi_control == 1
    assert mapping.pipewire_node_id == 42
    assert mapping.pipewire_node_name == "Test Node"


def test_midi_device_to_dict():
    """Test MidiDevice serialization"""
    device = MidiDevice(name="Test MIDI", port=0)
    
    data = device.to_dict()
    
    assert data['name'] == "Test MIDI"
    assert data['port'] == 0


def test_pipewire_node_to_dict():
    """Test PipewireNode serialization"""
    node = PipewireNode(
        node_id=42,
        name="Test Node",
        description="Test Description",
        media_class="Audio/Sink"
    )
    
    data = node.to_dict()
    
    assert data['node_id'] == 42
    assert data['name'] == "Test Node"
    assert data['description'] == "Test Description"
    assert data['media_class'] == "Audio/Sink"
