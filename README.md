# TimeTap

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
import threading
import TimeTap  # package exposes timing utilities


@TimeTap.timeTap_log(name="compute-sum")
def compute_sum(n=1_000_000):
    total = 0
    for i in range(n):
        total += i
    return total

with TimeTap.timeTap_log("session"):
    compute_sum()
    time.sleep(0.1)
    compute_sum()
    # You can temporarily disable collection any time
    TimeTap.disable_timeTap()
    time.sleep(0.1)
    compute_sum()
    # And re-enable
    TimeTap.enable_timeTap()
    time.sleep(0.1)
    compute_sum()

# Get a pretty, hierarchical report
print(TimeTap.timeTap_get_str())
# Or print directly
TimeTap.timeTap_print()

# Reset collected metrics
TimeTap.timeTap_reset()
```

```
RESULT
```

## Nested & GPU timing

```
# Nested sections automatically appear as a hierarchy in the report
with TimeTap.timeTap_log("pipeline"):
    with TimeTap.timeTap_log("stage-1"):
        time.sleep(0.05)

    # If installed with timetap[torch], set gpu=True to time CUDA work
    with TimeTap.timeTap_log("forward-pass", gpu=True):
        # Example (pseudo-code):
        # out = model(x); loss = out.sum(); loss.backward()
        time.sleep(0.02)  # placeholder for GPU work

TimeTap.timeTap_print()
```
> Tip: When gpu=True and PyTorch is available, TimeTap accounts for CUDA work so your timings include GPU kernels.

```
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
name = "TimeTap"
version = "0.1.0"
description = "A lightweight, thread-safe Python profiler for hierarchical code timing with GPU support"
readme = "README.md"
requires-python = ">=3.8"
dependencies = []

[project.optional-dependencies]
torch = ["torch>=2.1.0"]
```