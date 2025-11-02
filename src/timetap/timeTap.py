from contextlib import contextmanager
from timetap.TimeTapHelperClass import TimeTapHelperClass


@contextmanager
def log(name: str, enable=True, verbose=False, gpu=False) -> None:
    """
    Public context manager for timing a block of code and recording metrics.

    Convenience wrapper that delegates to the singleton TimeTapHelperClass().log.

    Use as:
        with timeTap_log("name"):
            code to measure

    Parameters:
        name (str): Label for the timing scope.
        enable (bool): If False, context becomes a no-op.
        verbose (bool): If True, prints an immediate timing line for the scope.
        gpu (bool): If True and torch is available, performs CUDA synchronization.

    Yields:
        None
    """
    return TimeTapHelperClass().log(
        name=name,
        enable=enable,
        verbose=verbose,
        gpu=gpu,
    )


def get_table_str() -> str:
    """
    Return the current metrics report as a formatted string.

    Fetches and returns the human-readable representation of all collected
    timing metrics. Does not modify the recorded data.

    Returns:
        str: Formatted metrics report suitable for printing or logging.
    """
    return TimeTapHelperClass().str_metrics()


def print_table() -> None:
    """
    Print the current metrics report to stdout.

    Convenience function that calls timeTap_get_str() and prints its value.
    """
    print(get_table_str())


def reset() -> None:
    """
    Reset and clear all recorded timing metrics.

    Delegates to the singleton's reset method. After calling this, subsequent
    timings begin from a clean state.
    """
    TimeTapHelperClass().reset()


def disable():
    """
    Disable all timing measurements globally.

    Sets the internal flag to disable timing, causing all subsequent
    timeTap_log contexts to become no-ops until re-enabled.
    """
    TimeTapHelperClass().set_enabled(False)


def enable():
    """
    Enable all timing measurements globally.

    Sets the internal flag to enable timing, resuming all subsequent
    timeTap_log contexts.
    """
    TimeTapHelperClass().set_enabled(True)
