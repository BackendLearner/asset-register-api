from decorators import timing, retry
import pytest


def test_timing(capsys):
    @timing
    def sample_function():
        return "success"

    result = sample_function()

    assert result == "success"

    captured = capsys.readouterr()

    assert "sample_function took" in captured.out


def test_retry_success():
    attempts = 0

    @retry(times=3, delay=0)
    def sample_function():
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            raise TimeoutError("Temporary failure")

        return "success"

    result = sample_function()

    assert result == "success"
    assert attempts == 3    

def test_retry_all_attempts_fail():
    attempts = 0

    @retry(times=3, delay=0)
    def sample_function():
        nonlocal attempts
        attempts += 1
        raise TimeoutError("Server is unavailable")

    with pytest.raises(TimeoutError, match="Server is unavailable"):
        sample_function()

    assert attempts == 3    

def test_retry_does_not_retry_unselected_exception():
    attempts = 0

    @retry(times=3, delay=0)
    def sample_function():
        nonlocal attempts
        attempts += 1
        raise ValueError("Invalid input")

    with pytest.raises(ValueError, match="Invalid input"):
        sample_function()

    assert attempts == 1 
    

def test_timing_prints_time_when_function_fails(capsys):
    @timing
    def sample_function():
        raise ValueError("Something went wrong")

    with pytest.raises(ValueError, match="Something went wrong"):
        sample_function()

    captured = capsys.readouterr()
    assert "sample_function took" in captured.out
    

def test_decorator_preserves_function_name():
    @timing
    def sample_function():
        """Sample function."""
        return "success"

    assert sample_function.__name__ == "sample_function"
    assert sample_function.__doc__ == "Sample function."           