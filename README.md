# TimeTap - Tap Into Runtime

A lightweight, thread-safe Python profiler for hierarchical code timing — with optional GPU support.

- Hierarchical timings: nest blocks, functions, and lines.
- Two ways to use: decorator or with context manager.
- Thread-safe: collect timings across threads.
- Optional GPU support to measure PyTorch CUDA sections (install extra).
- Easy reporting: print or get a formatted string; reset anytime.

## Installation

```
# CPU-only
pip install timetap

# With GPU helpers (PyTorch >= 2.1)
pip install "timetap[torch]"
```

## Quick start

```
import time
import timetap  # package exposes timing utilities


@timetap.timeTap_log(name="compute-sum")
def compute_sum(n=1_000_000):
    total = 0
    for i in range(n):
        total += i
    return total


with timetap.timeTap_log("session"):
    compute_sum()
    time.sleep(0.1)
    compute_sum()


# Or print directly
timetap.timeTap_print()

# Reset collected metrics
timetap.timeTap_reset()

with timetap.timeTap_log("session-2"):
    compute_sum()

    # You can temporarily disable collection any time
    timetap.disable_timeTap()
    time.sleep(0.1)
    compute_sum()

    # And re-enable all again
    timetap.enable_timeTap()
    time.sleep(0.1)
    compute_sum()

timetap.timeTap_print()
```

#### Output:
```
-----------------------------------------------------------------------------------------------
Function                 Runs    Total(ms)   Median(ms)      Avg(ms)      Min(ms)      Max(ms)
-----------------------------------------------------------------------------------------------
session                    1        132.6        132.6        132.6        132.6        132.6
└─compute-sum              2         32.4         16.2         16.2         16.2         16.2

WARNING:root:Disabling TimeTap timing measurements globally.
-----------------------------------------------------------------------------------------------
Function                 Runs    Total(ms)   Median(ms)      Avg(ms)      Min(ms)      Max(ms)
-----------------------------------------------------------------------------------------------
session-2                  1        250.9        250.9        250.9        250.9        250.9
└─compute-sum              2         33.7         16.8         16.8         16.7         17.0
```

## Nested & GPU timing

```
import time
import timetap

# Nested sections automatically appear as a hierarchy in the report
with timetap.timeTap_log("pipeline"):
    with timetap.timeTap_log("stage-1"):
        with timetap.timeTap_log("stage-2"):
            with timetap.timeTap_log("stage-3"):
                time.sleep(0.1)
            time.sleep(0.1)
        time.sleep(0.05)

    # If installed with timetap[torch], set gpu=True to time CUDA work
    with timetap.timeTap_log("forward-pass", gpu=True):
        time.sleep(0.02)

timetap.timeTap_print()
```
> Tip: When gpu=True and PyTorch is available, TimeTap accounts for CUDA work so your timings include GPU kernels.

#### Output:
```
-----------------------------------------------------------------------------------------------
Function                 Runs    Total(ms)   Median(ms)      Avg(ms)      Min(ms)      Max(ms)
-----------------------------------------------------------------------------------------------
pipeline                   1        270.6        270.6        270.6        270.6        270.6
├─stage-1                  1        250.4        250.4        250.4        250.4        250.4
├───stage-2                1        200.2        200.2        200.2        200.2        200.2
├─────stage-3              1        100.1        100.1        100.1        100.1        100.1
└─forward-pass             1         20.1         20.1         20.1         20.1         20.1
```

## API

All functions are available off the TimeTap package:

- timeTap_log(name: str, enable: bool = True, verbose: bool = False, gpu: bool = False)
    - Decorator or context manager for timing.
    - As a decorator: @TimeTap.timeTap_log(name="...")
    - As a context manager: with TimeTap.timeTap_log("..."): ...

- timeTap_get_str() -> str
Get a formatted, hierarchical summary of collected timings.

- timeTap_print() -> None
Print the current summary to stdout.

- timeTap_reset() -> None
Clear all collected metrics.

- disable_timeTap() / enable_timeTap()
Globally toggle collection (no-op when disabled).

## Project metadata
```
[project]
name = "timetap"
version = "0.1.0"
description = "A lightweight, thread-safe Python profiler for hierarchical code timing with GPU support"
readme = "README.md"
requires-python = ">=3.8"
dependencies = []

[project.optional-dependencies]
torch = ["torch>=2.1.0"]
```