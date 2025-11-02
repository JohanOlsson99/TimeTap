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
timetap.timeTap_reset()


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
