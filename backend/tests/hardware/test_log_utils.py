"""Unit tests for the logging utilities."""
import json
import os
import tempfile

from hardware.utils.logger import EdgeLogger, logger


def test_logger_initialization():
    """Test logger initialization with different log levels."""
    # Test with default log level (INFO)
    default_logger = EdgeLogger()
    assert default_logger.log_level == 20  # INFO level
    
    # Test with custom log level
    debug_logger = EdgeLogger(log_level='DEBUG')
    assert debug_logger.log_level == 10  # DEBUG level
    
    # Test with invalid log level (should default to INFO)
    invalid_logger = EdgeLogger(log_level='INVALID')
    assert invalid_logger.log_level == 20  # Default to INFO


def test_log_levels():
    """Test that log levels work as expected."""
    log = EdgeLogger(log_level='WARNING')
    
    # These should not be logged due to log level
    log.debug("Debug message")
    log.info("Info message")
    
    # These should be logged
    log.warning("Warning message")
    log.error("Error message")
    log.critical("Critical message")
    
    # Only 3 messages should be logged (WARNING, ERROR, CRITICAL)
    logs = log.get_logs()
    assert len(logs) == 3
    assert logs[0]['level'] == 'WARNING'
    assert logs[1]['level'] == 'ERROR'
    assert logs[2]['level'] == 'CRITICAL'


def test_log_extra_data():
    """Test logging with extra data."""
    log = EdgeLogger()
    extra_data = {
        'key1': 'value1',
        'key2': 123,
        'key3': {'nested': 'data'}
    }
    
    log.info("Test message with extra data", **extra_data)
    logs = log.get_logs()
    
    assert len(logs) == 1
    log_entry = logs[0]
    assert log_entry['message'] == "Test message with extra data"
    assert log_entry['key1'] == 'value1'
    assert log_entry['key2'] == 123
    assert log_entry['key3'] == {'nested': 'data'}


def test_log_rotation():
    """Test that log rotation works as expected."""
    log = EdgeLogger(max_entries=3)
    
    # Add more entries than the max
    for i in range(5):
        log.info(f"Message {i}")
    
    # Should only keep the most recent 3 entries
    logs = log.get_logs()
    assert len(logs) == 3
    assert logs[0]['message'] == "Message 2"
    assert logs[1]['message'] == "Message 3"
    assert logs[2]['message'] == "Message 4"


def test_flush_to_console(capsys):
    """Test flushing logs to console."""
    log = EdgeLogger()
    log.info("Test console message", extra={'key': 'value'})
    log.flush_to_console()
    
    captured = capsys.readouterr()
    assert "[INFO] Test console message" in captured.out


def test_flush_to_file():
    """Test flushing logs to a file."""
    log = EdgeLogger()
    log.info("Test file message", extra={'key': 'value'})
    
    with tempfile.NamedTemporaryFile(delete=False, mode='w+') as temp_file:
        try:
            log.flush_to_file(temp_file.name)
            
            # Read the file and verify contents
            with open(temp_file.name, 'r') as f:
                lines = f.readlines()
                assert len(lines) == 1
                log_entry = json.loads(lines[0])
                assert log_entry['message'] == "Test file message"
                assert log_entry['key'] == 'value'
        finally:
            # Clean up
            try:
                os.unlink(temp_file.name)
            except:
                pass


def test_clear_logs():
    """Test clearing the log buffer."""
    log = EdgeLogger()
    log.info("Test message")
    
    assert len(log.get_logs()) == 1
    log.clear()
    assert len(log.get_logs()) == 0


def test_default_logger():
    """Test that the default logger is properly initialized."""
    assert isinstance(logger, EdgeLogger)
    assert logger.log_level == 20  # Default to INFO
    
    # Test that we can log using the default logger
    logger.info("Test default logger")
    logs = logger.get_logs()
    assert len(logs) >= 1  # Could be more if other tests used the logger
    assert any(log['message'] == "Test default logger" for log in logs)
