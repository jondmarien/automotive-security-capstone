"""Logging utilities for the edge device."""
import json
import time
from collections import deque
from typing import Any, Dict, List


class EdgeLogger:
    """Simple logging system for edge devices with log rotation.
    
    This logger stores logs in memory and can flush them to a file or console.
    It's designed to work in resource-constrained environments.
    """
    
    LOG_LEVELS = {
        'DEBUG': 10,
        'INFO': 20,
        'WARNING': 30,
        'ERROR': 40,
        'CRITICAL': 50
    }
    
    def __init__(self, max_entries: int = 1000, log_level: str = 'INFO'):
        """Initialize the logger.
        
        Args:
            max_entries: Maximum number of log entries to keep in memory
            log_level: Minimum log level to record
        """
        self.max_entries = max_entries
        self.log_level = self.LOG_LEVELS.get(log_level.upper(), 20)  # Default to INFO
        self.log_buffer = deque(maxlen=max_entries)
    
    def _should_log(self, level: str) -> bool:
        """Check if a message at the given level should be logged."""
        return self.LOG_LEVELS.get(level.upper(), 0) >= self.log_level
    
    def _log(self, level: str, message: str, **extra: Any) -> None:
        """Internal method to handle the actual logging."""
        if not self._should_log(level):
            return
            
        log_entry = {
            'timestamp': time.time(),
            'level': level.upper(),
            'message': message
        }
        
        # Include extra data if provided - handle both direct and nested 'extra' dict
        if extra:
            if 'extra' in extra and isinstance(extra['extra'], dict):
                log_entry.update(extra['extra'])
            else:
                log_entry.update(extra)
            
        self.log_buffer.append(log_entry)
    
    def debug(self, message: str, **extra: Any) -> None:
        """Log a debug message."""
        self._log('DEBUG', message, **extra)
    
    def info(self, message: str, **extra: Any) -> None:
        """Log an info message."""
        self._log('INFO', message, **extra)
    
    def warning(self, message: str, **extra: Any) -> None:
        """Log a warning message."""
        self._log('WARNING', message, **extra)
    
    def error(self, message: str, **extra: Any) -> None:
        """Log an error message."""
        self._log('ERROR', message, **extra)
    
    def critical(self, message: str, **extra: Any) -> None:
        """Log a critical message."""
        self._log('CRITICAL', message, **extra)
    
    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent log entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of log entries, most recent first
        """
        return list(self.log_buffer)[-limit:]
    
    def flush_to_console(self) -> None:
        """Print all logs to the console."""
        for entry in self.log_buffer:
            print(f"[{entry['level']}] {entry['message']}")
            if 'extra' in entry:
                print(f"  Extra: {entry['extra']}")
    
    def flush_to_file(self, filename: str) -> None:
        """Write all logs to a file.
        
        Args:
            filename: Path to the output file
        """
        with open(filename, 'a') as f:
            for entry in self.log_buffer:
                f.write(json.dumps(entry) + '\n')
    
    def clear(self) -> None:
        """Clear all log entries."""
        self.log_buffer.clear()

# Create a default logger instance
logger = EdgeLogger()
