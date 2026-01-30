"""Tests for configuration management"""

import tempfile
import os
from pathlib import Path

from midixer.common.config import Config
from midixer.common.models import MidiMapping


def test_config_initialization():
    """Test Config initialization"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"
        config = Config(str(config_path))

        assert config.config_path == config_path
        assert config.mappings == []
        assert config_path.exists()


def test_config_add_mapping():
    """Test adding a mapping"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"
        config = Config(str(config_path))

        mapping = MidiMapping(
            midi_device="Test Device",
            midi_channel=0,
            midi_control=1,
            pipewire_node_id=42,
            pipewire_node_name="Test Node",
        )

        config.add_mapping(mapping)

        assert len(config.mappings) == 1
        assert config.mappings[0].midi_device == "Test Device"


def test_config_remove_mapping():
    """Test removing a mapping"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"
        config = Config(str(config_path))

        mapping = MidiMapping(
            midi_device="Test Device",
            midi_channel=0,
            midi_control=1,
            pipewire_node_id=42,
            pipewire_node_name="Test Node",
        )

        config.add_mapping(mapping)
        config.remove_mapping(0)

        assert len(config.mappings) == 0


def test_config_persistence():
    """Test config persistence across instances"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"

        # Create and save config
        config1 = Config(str(config_path))
        mapping = MidiMapping(
            midi_device="Test Device",
            midi_channel=0,
            midi_control=1,
            pipewire_node_id=42,
            pipewire_node_name="Test Node",
        )
        config1.add_mapping(mapping)

        # Load config in new instance
        config2 = Config(str(config_path))

        assert len(config2.mappings) == 1
        assert config2.mappings[0].midi_device == "Test Device"


def test_config_get_mappings():
    """Test getting mappings returns a copy"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"
        config = Config(str(config_path))

        mapping = MidiMapping(
            midi_device="Test Device",
            midi_channel=0,
            midi_control=1,
            pipewire_node_id=42,
            pipewire_node_name="Test Node",
        )

        config.add_mapping(mapping)
        mappings = config.get_mappings()

        # Modifying the returned list shouldn't affect the config
        mappings.clear()
        assert len(config.mappings) == 1


def test_config_clear_mappings():
    """Test clearing all mappings"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"
        config = Config(str(config_path))

        mapping = MidiMapping(
            midi_device="Test Device",
            midi_channel=0,
            midi_control=1,
            pipewire_node_id=42,
            pipewire_node_name="Test Node",
        )

        config.add_mapping(mapping)
        config.clear_mappings()

        assert len(config.mappings) == 0
