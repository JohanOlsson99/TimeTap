import time

import timetap  # package exposes timing utilities


@timetap.log(name="compute-sum")
def compute_sum(n=1_000_000):
    total = 0
    for i in range(n):
        total += i
    return total


with timetap.log("session"):
    compute_sum()
    time.sleep(0.1)
    compute_sum()


# Or print directly
timetap.print_table()

# Reset collected metrics
timetap.reset()

with timetap.log("session-2"):
    compute_sum()

    # You can temporarily disable collection any time
    timetap.disable()
    time.sleep(0.1)
    compute_sum()

    # And re-enable all again
    timetap.enable()
    time.sleep(0.1)
    compute_sum()

timetap.print_table()
timetap.reset()


# Nested sections automatically appear as a hierarchy in the report
with timetap.log("pipeline"):
    with timetap.log("stage-1"):
        with timetap.log("stage-2"):
            with timetap.log("stage-3"):
                time.sleep(0.1)
            time.sleep(0.1)
        time.sleep(0.05)

    # If installed with timetap[torch], set gpu=True to time CUDA work
    with timetap.log("forward-pass", gpu=True):
        time.sleep(0.02)

timetap.print_table()
