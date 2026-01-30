"""Pipewire/Wireplumber controller for volume management"""

import subprocess
from typing import List, Optional
from ..common.models import PipewireNode


class PipewireController:
    """Controls Pipewire node volumes via wpctl"""

    def __init__(self):
        """Initialize Pipewire controller"""
        pass

    def get_nodes(self) -> List[PipewireNode]:
        """
        Get list of Pipewire audio nodes

        Returns:
            List of PipewireNode objects
        """
        nodes = []

        try:
            # Use wpctl to list audio nodes
            result = subprocess.run(["wpctl", "status"], capture_output=True, text=True, timeout=5)

            if result.returncode != 0:
                print(f"Error getting Pipewire nodes: {result.stderr}")
                return nodes

            # Parse output (simplified - in production would need more robust parsing)
            # This is a starter implementation
            lines = result.stdout.split("\n")
            in_audio_section = False

            for line in lines:
                if "Audio" in line or "Sinks" in line or "Sources" in line:
                    in_audio_section = True
                    continue

                if in_audio_section and "│" in line:
                    # Parse node line (format: "│  ├─ ID. Name")
                    parts = line.split(".")
                    if len(parts) >= 2:
                        try:
                            # Extract node ID
                            id_part = parts[0].strip().split()[-1]
                            node_id = int(id_part)

                            # Extract name
                            name = parts[1].strip()

                            nodes.append(
                                PipewireNode(
                                    node_id=node_id,
                                    name=name,
                                    description=name,
                                    media_class="Audio",
                                )
                            )
                        except (ValueError, IndexError):
                            continue

        except subprocess.TimeoutExpired:
            print("Timeout getting Pipewire nodes")
        except FileNotFoundError:
            print("wpctl not found - is Wireplumber installed?")
        except Exception as e:
            print(f"Error getting Pipewire nodes: {e}")

        return nodes

    def set_volume(self, node_id: int, volume: float) -> bool:
        """
        Set volume for a Pipewire node

        Args:
            node_id: Pipewire node ID
            volume: Volume level (0.0 to 1.0)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Clamp volume to valid range
            volume = max(0.0, min(1.0, volume))

            # Convert to percentage string for wpctl
            volume_percent = f"{volume * 100:.0f}%"

            # Use wpctl to set volume
            result = subprocess.run(
                ["wpctl", "set-volume", str(node_id), volume_percent],
                capture_output=True,
                timeout=2,
            )

            return result.returncode == 0

        except Exception as e:
            print(f"Error setting volume for node {node_id}: {e}")
            return False

    def get_volume(self, node_id: int) -> Optional[float]:
        """
        Get current volume for a Pipewire node

        Args:
            node_id: Pipewire node ID

        Returns:
            Volume level (0.0 to 1.0) or None if error
        """
        try:
            result = subprocess.run(
                ["wpctl", "get-volume", str(node_id)], capture_output=True, text=True, timeout=2
            )

            if result.returncode == 0:
                # Parse output (format: "Volume: 0.50")
                output = result.stdout.strip()
                if "Volume:" in output:
                    volume_str = output.split(":")[1].strip()
                    return float(volume_str)

            return None

        except Exception as e:
            print(f"Error getting volume for node {node_id}: {e}")
            return None
