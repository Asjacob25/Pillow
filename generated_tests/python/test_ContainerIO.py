import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from unittest.mock import MagicMock
from src.PIL.ContainerIO import ContainerIO

@pytest.fixture
def mock_file():
    file = MagicMock()
    file.read.return_value = "test"
    file.mode = 'r'
    return file

@pytest.fixture
def container_io(mock_file):
    return ContainerIO(mock_file, 0, 10)


def test_container_io_initialization(mock_file):
    """Test ContainerIO is correctly initialized."""
    cio = ContainerIO(mock_file, 100, 200)
    assert cio.offset == 100
    assert cio.length == 200
    assert cio.pos == 0
    mock_file.seek.assert_called_once_with(100)

def test_seek_within_bounds(container_io):
    """Test seeking within the bounds moves the file pointer correctly."""
    assert container_io.seek(5) == 5
    assert container_io.pos == 5

def test_seek_beyond_bounds(container_io):
    """Test seeking beyond the bounds clamps to the boundary."""
    assert container_io.seek(11) == 10
    assert container_io.pos == 10

def test_seek_with_mode(container_io):
    """Test seeking with different modes works as expected."""
    container_io.seek(5)  # Move to position 5
    container_io.seek(2, mode=1)  # Move 2 bytes from current position
    assert container_io.pos == 7
    container_io.seek(-3, mode=2)  # Move to 3 bytes before the end
    assert container_io.pos == 7

def test_tell_reports_current_position(container_io):
    """Test tell() returns the current file pointer."""
    container_io.seek(3)
    assert container_io.tell() == 3

def test_read_within_bounds(container_io):
    """Test reading within bounds returns correct data."""
    container_io.fh.read.return_value = "test"
    assert container_io.read(4) == "test"

def test_read_beyond_bounds(container_io, mock_file):
    """Test reading beyond bounds returns data up to the boundary."""
    mock_file.read.return_value = "testtest"
    container_io.seek(8)
    assert container_io.read(5) == "test"
    assert container_io.pos == 10

def test_readline_reads_correctly(container_io):
    """Test readline() reads a line correctly."""
    container_io.fh.read.side_effect = ["t", "e", "s", "t", "\n", "extra"]
    assert container_io.readline() == "test\n"
    assert container_io.pos == 5

def test_readlines_reads_all_lines(container_io):
    """Test readlines() reads all lines correctly."""
    container_io.fh.read.side_effect = ["t", "e", "s", "t", "\n", "d", "o", "n", "e", "\n"]
    assert container_io.readlines() == ["test\n", "done\n"]

def test_readlines_with_limit(container_io):
    """Test readlines() respects the limit."""
    container_io.fh.read.side_effect = ["t", "e", "s", "t", "\n", "d", "o", "n", "e", "\n"]
    assert container_io.readlines(n=1) == ["test\n"]

def test_writable_returns_false(container_io):
    """Test writable() should always return False."""
    assert not container_io.writable()

def test_write_raises_not_implemented_error(container_io):
    """Test write() raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        container_io.write("test")

def test_writelines_raises_not_implemented_error(container_io):
    """Test writelines() raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        container_io.writelines(["test"])

def test_seekable_always_true(container_io):
    """Test seekable() should always return True."""
    assert container_io.seekable()

def test_flush_calls_underlying_flush(container_io):
    """Test flush calls the underlying file's flush method."""
    container_io.flush()
    container_io.fh.flush.assert_called_once()

def test_close_calls_underlying_close(container_io):
    """Test close calls the underlying file's close method."""
    container_io.close()
    container_io.fh.close.assert_called_once()

def test_isatty_always_false(container_io):
    """Test isatty() should always return False."""
    assert not container_io.isatty()

def test_fileno_calls_underlying_fileno(container_io):
    """Test fileno calls the underlying file's fileno method."""
    container_io.fileno()
    container_io.fh.fileno.assert_called_once()

def test_context_manager(container_io, mock_file):
    """Test ContainerIO can be used as a context manager."""
    with container_io as cio:
        assert cio == container_io
    mock_file.close.assert_called_once()