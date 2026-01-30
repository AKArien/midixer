"""Configuration management for midixer"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from .models import MidiMapping


class Config:
    """Manages midixer configuration"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize configuration
        
        Args:
            config_path: Path to config file. Defaults to ~/.config/midixer/config.json
        """
        if config_path is None:
            config_dir = Path.home() / ".config" / "midixer"
            config_dir.mkdir(parents=True, exist_ok=True)
            config_path = config_dir / "config.json"
        
        self.config_path = Path(config_path)
        self.mappings: List[MidiMapping] = []
        self.load()
    
    def load(self) -> None:
        """Load configuration from file"""
        if not self.config_path.exists():
            self.save()  # Create default config
            return
        
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                self.mappings = [
                    MidiMapping.from_dict(m) for m in data.get('mappings', [])
                ]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading config: {e}")
            self.mappings = []
    
    def save(self) -> None:
        """Save configuration to file"""
        data = {
            'mappings': [m.to_dict() for m in self.mappings]
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_mapping(self, mapping: MidiMapping) -> None:
        """Add a new MIDI mapping"""
        self.mappings.append(mapping)
        self.save()
    
    def remove_mapping(self, index: int) -> None:
        """Remove a MIDI mapping by index"""
        if 0 <= index < len(self.mappings):
            self.mappings.pop(index)
            self.save()
    
    def get_mappings(self) -> List[MidiMapping]:
        """Get all mappings"""
        return self.mappings.copy()
    
    def clear_mappings(self) -> None:
        """Clear all mappings"""
        self.mappings.clear()
        self.save()
