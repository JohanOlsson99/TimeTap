import time
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


# Or print directly
TimeTap.timeTap_print()

# Reset collected metrics
TimeTap.timeTap_reset()

with TimeTap.timeTap_log("session-2"):
    compute_sum()

    # You can temporarily disable collection any time
    TimeTap.disable_timeTap()
    time.sleep(0.1)
    compute_sum()

    # And re-enable all again
    TimeTap.enable_timeTap()
    time.sleep(0.1)
    compute_sum()

TimeTap.timeTap_print()
TimeTap.timeTap_reset()


# Nested sections automatically appear as a hierarchy in the report
with TimeTap.timeTap_log("pipeline"):
    with TimeTap.timeTap_log("stage-1"):
        with TimeTap.timeTap_log("stage-2"):
            with TimeTap.timeTap_log("stage-3"):
                time.sleep(0.1)
            time.sleep(0.1)
        time.sleep(0.05)

    # If installed with timetap[torch], set gpu=True to time CUDA work
    with TimeTap.timeTap_log("forward-pass", gpu=True):
        time.sleep(0.02)

TimeTap.timeTap_print()
