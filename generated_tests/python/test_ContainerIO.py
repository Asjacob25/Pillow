import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import io
import pytest
from unittest.mock import MagicMock
from src.PIL.ContainerIO import ContainerIO

@pytest.fixture
def setup_file_mock():
    file_mock = MagicMock(spec=io.BytesIO)
    file_mock.read.return_value = b"Test data"
    file_mock.mode = 'rb'
    return file_mock

@pytest.fixture
def container_io_instance(setup_file_mock):
    return ContainerIO(setup_file_mock, 0, 10)

def test_seek_within_bounds(container_io_instance):
    """Test seeking within the bounds of the ContainerIO region."""
    assert container_io_instance.seek(5) == 5
    assert container_io_instance.tell() == 5

def test_seek_out_of_bounds(container_io_instance):
    """Test seeking outside the bounds of the ContainerIO region."""
    assert container_io_instance.seek(-5) == 0
    assert container_io_instance.seek(15, mode=2) == 10
    assert container_io_instance.tell() == 10

def test_read_within_bounds(container_io_instance):
    """Test reading within the bounds of the ContainerIO region."""
    container_io_instance.seek(0)
    data = container_io_instance.read(4)
    assert data == b"Test"
    assert container_io_instance.tell() == 4

def test_read_beyond_bounds(container_io_instance):
    """Test reading beyond the bounds of the ContainerIO region."""
    container_io_instance.seek(0)
    data = container_io_instance.read(20)
    assert len(data) == 10  # As the mock returns "Test data"
    assert container_io_instance.tell() == 10

def test_readline(container_io_instance):
    """Test reading a single line."""
    container_io_instance.seek(0)
    line = container_io_instance.readline()
    assert line == b"Test data"

def test_readlines(container_io_instance):
    """Test reading multiple lines."""
    container_io_instance.seek(0)
    lines = container_io_instance.readlines()
    assert lines == [b"Test data"]

def test_iter_and_next(container_io_instance):
    """Test the iterator protocol implementation."""
    container_io_instance.seek(0)
    lines = list(container_io_instance)
    assert lines == [b"Test data"]

def test_readlines_with_limit(container_io_instance):
    """Test reading a limited number of lines."""
    container_io_instance.seek(0)
    lines = container_io_instance.readlines(1)
    assert lines == [b"Test data"]
    assert len(lines) == 1

def test_not_writable(container_io_instance):
    """Test that ContainerIO is not writable."""
    assert not container_io_instance.writable()

def test_write_not_implemented(container_io_instance):
    """Test that write operation is not implemented."""
    with pytest.raises(NotImplementedError):
        container_io_instance.write(b"Some data")

def test_writelines_not_implemented(container_io_instance):
    """Test that writelines operation is not implemented."""
    with pytest.raises(NotImplementedError):
        container_io_instance.writelines([b"Some data"])

def test_truncate_not_implemented(container_io_instance):
    """Test that truncate operation is not implemented."""
    with pytest.raises(NotImplementedError):
        container_io_instance.truncate()

def test_context_manager(container_io_instance, setup_file_mock):
    """Test ContainerIO used as a context manager."""
    with container_io_instance as container:
        assert container.read() == b"Test data"
    setup_file_mock.close.assert_called_once()

def test_fileno(container_io_instance, setup_file_mock):
    """Test getting the file descriptor."""
    setup_file_mock.fileno.return_value = 3
    assert container_io_instance.fileno() == 3
    setup_file_mock.fileno.assert_called_once()

def test_flush(container_io_instance, setup_file_mock):
    """Test flushing the IO object."""
    container_io_instance.flush()
    setup_file_mock.flush.assert_called_once()

def test_close(container_io_instance, setup_file_mock):
    """Test closing the ContainerIO object."""
    container_io_instance.close()
    setup_file_mock.close.assert_called_once()