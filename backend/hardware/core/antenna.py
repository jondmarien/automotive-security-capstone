"""Antenna selection and management for the edge device."""

class AntennaManager:
    """Manages antenna selection and configuration.
    
    This class provides functionality to manage different antennas
    and their configurations for the edge device.
    """
    
    def __init__(self):
        """Initialize the antenna manager."""
        self.active_antenna = None
        self.available_antennas = []
    
    def list_antennas(self) -> list:
        """List all available antennas.
        
        Returns:
            List of available antenna names
        """
        return self.available_antennas
    
    def select_antenna(self, antenna_name: str) -> bool:
        """Select an antenna to use.
        
        Args:
            antenna_name: Name of the antenna to select
            
        Returns:
            bool: True if selection was successful, False otherwise
        """
        if antenna_name in self.available_antennas:
            self.active_antenna = antenna_name
            return True
        return False
    
    def get_active_antenna(self) -> str:
        """Get the currently active antenna.
        
        Returns:
            Name of the active antenna, or None if none selected
        """
        return self.active_antenna
    
    def add_antenna(self, antenna_name: str) -> bool:
        """Add a new antenna to the available list.
        
        Args:
            antenna_name: Name of the antenna to add
            
        Returns:
            bool: True if added, False if already exists
        """
        if antenna_name not in self.available_antennas:
            self.available_antennas.append(antenna_name)
            return True
        return False
