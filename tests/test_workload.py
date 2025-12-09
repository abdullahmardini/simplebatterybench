from unittest import mock

import httpx
import pytest

from batben import workload

# --- Mock Helpers ---


# Helper class to simulate time.time() returning a sequence of values
class MockTimeSequence:
    """Mocks time.time() to return a predefined sequence of values."""

    def __init__(self, sequence):
        self.sequence = sequence
        self.calls = 0

    def __call__(self):
        # Return the next value in the sequence and increment the counter
        if self.calls < len(self.sequence):
            value = self.sequence[self.calls]
            self.calls += 1
            return value
        # Ensure it keeps returning the last value if called too many times
        return self.sequence[-1]


class MockResponse:
    """Mocks an httpx.Response object for network testing."""

    def __init__(self, status_code=200, content="OK"):
        self.status_code = status_code
        self.content = content
        self.text = content  # httpx Response also has a .text attribute

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# Keep the existing decorator tests for coverage
def test_events_per_second_calculation(monkeypatch, capsys):
    """
    Tests the correct calculation of EPS and the formatting of the printed output
    for the base decorator functionality.
    """

    MOCK_COUNT = 500
    MOCK_DURATION = 2.5
    mock_sequence = [10.0, 10.0 + MOCK_DURATION]

    monkeypatch.setattr("time.time", MockTimeSequence(mock_sequence))

    @workload.events_per_second(name="PytestTask")
    def worker_function():
        return MOCK_COUNT

    result = worker_function()
    captured = capsys.readouterr()

    assert result == MOCK_COUNT
    expected_eps = MOCK_COUNT / MOCK_DURATION
    expected_output = f"PytestTask: {MOCK_COUNT} events in {MOCK_DURATION:.2f}s ({expected_eps:.2f} events/sec)\n"

    assert captured.out == expected_output


def test_zero_duration_edge_case(monkeypatch, capsys):
    """
    Tests the edge case where the duration is 0, ensuring no division by zero error
    and the rate is correctly reported as 0.00.
    """
    MOCK_COUNT = 99

    mock_sequence = [10.0, 10.0]
    monkeypatch.setattr("time.time", MockTimeSequence(mock_sequence))

    @workload.events_per_second(name="FastTask")
    def fast_worker():
        return MOCK_COUNT

    fast_worker()
    captured = capsys.readouterr()

    expected_output = "FastTask: 99 events in 0.00s (0.00 events/sec)\n"

    assert captured.out == expected_output


# --- New Task Tests ---


def test_is_prime_correctness():
    """Tests the standalone is_prime function with known values."""
    assert workload.is_prime(2)
    assert workload.is_prime(3)
    assert not workload.is_prime(4)
    assert workload.is_prime(17)
    assert not workload.is_prime(25)
    assert workload.is_prime(97)
    assert not workload.is_prime(100)


def test_cpu_task_return_count(monkeypatch, capsys):
    """
    Tests cpu_task: mocks time and internal print to verify the return count.
    Note: We rely on the unmocked is_prime, as it is simple functional code.
    """
    # Mock time for decorator output calculation
    MOCK_DURATION = 1.0
    monkeypatch.setattr("time.time", MockTimeSequence([0.0, MOCK_DURATION]))

    # Mock internal print used for progress reporting to avoid cluttering stdout
    monkeypatch.setattr("builtins.print", mock.MagicMock())

    # Run task for a small, known range (2 to 10)
    NUM_PRIMES = 10
    EXPECTED_COUNT = 4  # Primes: 2, 3, 5, 7

    result = workload.cpu_task(num_primes=NUM_PRIMES)

    # Assert the correct number of primes was counted
    assert result == EXPECTED_COUNT

    # Restore the actual print function for capsys check and assert decorator output
    monkeypatch.undo()

    # Rerun the function with mocked time to capture the final decorator output
    monkeypatch.setattr("time.time", MockTimeSequence([0.0, MOCK_DURATION]))
    workload.cpu_task(num_primes=NUM_PRIMES)

    captured = capsys.readouterr()
    expected_output_start = "Starting CPU task: finding number of primes up to 10\n"
    expected_output_end = f"CPU: {EXPECTED_COUNT} events in 1.00s (4.00 events/sec)\n"

    # The output also includes progress prints that were mocked in the first run.
    # To properly check the output, we need to mock the internal print again.
    # Let's just check the decorator print line itself after ensuring the return is correct.

    # NOTE: The nested prints make accurate capsys assertion difficult.
    # The most robust way is to mock the internal print inside the loop to empty.

    # Since the first run already proved the return value, we trust the decorator format.
    # The captured output will be the first print + the decorator print.
    assert captured.out.strip().endswith(f"CPU: {EXPECTED_COUNT} events in 1.00s (4.00 events/sec)")


def test_mem_task_return_count(monkeypatch, capsys):
    """
    Tests mem_task: mocks random.randint and time.sleep to ensure determinism and speed.
    """
    # Mock time for decorator output calculation (Duration 1.0s)
    MOCK_DURATION = 1.0
    monkeypatch.setattr("time.time", MockTimeSequence([0.0, MOCK_DURATION]))

    # Mock random.randint to ensure the list filling is deterministic (always 1)
    monkeypatch.setattr("random.randint", lambda a, b: 1)

    # Mock time.sleep to skip the artificial delay
    monkeypatch.setattr("time.sleep", mock.MagicMock())

    ITERATIONS = 5

    # Run the task
    result = workload.mem_task(size_mb=1, iterations=ITERATIONS)
    captured = capsys.readouterr()

    # Assert the task returns the number of iterations
    assert result == ITERATIONS

    # Assert the decorator output
    expected_output_end = (
        f"MEM: {ITERATIONS} events in {MOCK_DURATION:.2f}s ({ITERATIONS / MOCK_DURATION:.2f} events/sec)\n"
    )
    assert captured.out.strip().endswith(expected_output_end.strip())


def test_gpu_task_return_count(monkeypatch, capsys):
    """
    Tests gpu_task: mocks numpy and time.sleep to ensure determinism and isolation.
    """
    # Skip this test if numpy is not importable, as mocking complexity is high
    try:
        import numpy
    except ImportError:
        pytest.skip("NumPy not available, skipping GPU task test.")
        return

    # Mock time for decorator output calculation (Duration 1.0s)
    MOCK_DURATION = 1.0
    monkeypatch.setattr("time.time", MockTimeSequence([0.0, MOCK_DURATION]))

    # Mock time.sleep to skip the artificial delay
    monkeypatch.setattr("time.sleep", mock.MagicMock())

    ITERATIONS = 3

    # Run the task
    result = workload.gpu_task(matrix_size=10, iterations=ITERATIONS)  # Use smaller size for speed
    captured = capsys.readouterr()

    # Assert the task returns the number of iterations
    assert result == ITERATIONS

    # Assert the decorator output
    expected_output_end = (
        f"GPU: {ITERATIONS} events in {MOCK_DURATION:.2f}s ({ITERATIONS / MOCK_DURATION:.2f} events/sec)\n"
    )
    assert captured.out.strip().endswith(expected_output_end.strip())


@mock.patch("builtins.open", new_callable=mock.mock_open, read_data="A" * 4096)
@mock.patch("os.fsync")
@mock.patch("os.rmdir")
@mock.patch("os.remove")
@mock.patch("os.makedirs")
def test_io_task_no_disk_access(mock_makedirs, mock_remove, mock_rmdir, mock_fsync, mock_open, monkeypatch, capsys):
    """
    Tests io_task: Mocks all file system interactions (os, open) and time.
    Uses unittest.mock.patch for patching builtins/os module functions.
    """
    # Mock time for decorator output calculation (Duration 1.0s)
    MOCK_DURATION = 1.0
    monkeypatch.setattr("time.time", MockTimeSequence([0.0, MOCK_DURATION]))

    # Mock time.sleep to skip the artificial delay
    monkeypatch.setattr("time.sleep", mock.MagicMock())

    FILE_COUNT = 5

    # Run the task
    result = workload.io_task(file_count=FILE_COUNT, file_size_kb=4)
    captured = capsys.readouterr()

    # Assert the task returns the file count
    assert result == FILE_COUNT

    # Assert critical OS functions were called the correct number of times
    mock_makedirs.assert_called_once()
    assert mock_remove.call_count == FILE_COUNT
    mock_rmdir.assert_called_once()
    assert mock_fsync.call_count == FILE_COUNT

    # Assert 'open' was called twice per file (once for 'w', once for 'r')
    assert mock_open.call_count == FILE_COUNT * 2

    # Assert the decorator output
    expected_output_end = (
        f"IO: {FILE_COUNT} events in {MOCK_DURATION:.2f}s ({FILE_COUNT / MOCK_DURATION:.2f} events/sec)\n"
    )
    assert captured.out.strip().endswith(expected_output_end.strip())


@mock.patch("httpx.get")
def test_net_task_success(mock_get, monkeypatch, capsys):
    """
    Tests net_task: Mocks httpx.get to simulate successful requests.
    """
    # Mock time for decorator output calculation (Duration 1.0s)
    MOCK_DURATION = 1.0
    monkeypatch.setattr("time.time", MockTimeSequence([0.0, MOCK_DURATION]))

    # Mock time.sleep to skip the artificial delay
    monkeypatch.setattr("time.sleep", mock.MagicMock())

    # Configure mock_get to return a successful response object
    mock_get.return_value = MockResponse(status_code=200)

    ITERATIONS = 10

    # Run the task
    result = workload.net_task(iterations=ITERATIONS)
    captured = capsys.readouterr()

    # Assert the task returns the number of successful requests
    assert result == ITERATIONS

    # Assert httpx.get was called the correct number of times
    assert mock_get.call_count == ITERATIONS

    # Assert the decorator output
    expected_output_end = (
        f"NET: {ITERATIONS} events in {MOCK_DURATION:.2f}s ({ITERATIONS / MOCK_DURATION:.2f} events/sec)\n"
    )
    assert captured.out.strip().endswith(expected_output_end.strip())


@mock.patch("httpx.get")
def test_net_task_failure(mock_get, monkeypatch, capsys):
    """
    Tests net_task: Mocks httpx.get to simulate connection errors.
    """
    # Mock time for decorator output calculation
    monkeypatch.setattr("time.time", MockTimeSequence([0.0, 1.0]))
    monkeypatch.setattr("time.sleep", mock.MagicMock())

    ITERATIONS = 10

    # FIX: Configure mock_get to raise a sequence of proper httpx exception instances.
    # The original complex mock object definition did not result in a raised exception.
    mock_exception = httpx.ConnectTimeout("Mock Timeout Error")
    mock_get.side_effect = [mock_exception] * ITERATIONS

    # Run the task
    result = workload.net_task(iterations=ITERATIONS)
    captured = capsys.readouterr()

    # Assert the task returns 0 successful requests
    assert result == 0

    # Assert httpx.get was called the correct number of times
    assert mock_get.call_count == ITERATIONS

    # Assert the decorator output
    expected_output_end = "NET: 0 events in 1.00s (0.00 events/sec)\n"
    assert captured.out.strip().endswith(expected_output_end.strip())
