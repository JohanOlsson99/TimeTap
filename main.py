# from TimeTap import (
#     timeTap_log,
#     timeTap_get_str,
#     timeTap_print,
#     timeTap_reset,
#     disable_timeTap,
#     enable_timeTap,
# )
import TimeTap
import threading
import time

TimeTap.disable_timeTap()


@TimeTap.timeTap_log(
    name="Total time adsjdhsajdh ajsd hjashd jsa hdasjhd jashdasd 213321 asdkjha skj dhjashd jash djashd",
    enable=True,
)
def example_function():
    total = 0
    for i in range(1000000):
        total += i
    return total


with TimeTap.timeTap_log(
    "Total time adsjdhsajdh ajsd hjashd jsa hdasjhd jashdasd", enable=True
):
    example_function()
    time.sleep(1)
    example_function()

# print(TimeTapHelperClass().str_metrics())
# TimeTapHelperClass().print_metrics()
# TimeTapHelperClass().reset()
TimeTap.timeTap_reset()

with TimeTap.timeTap_log(
    "Total time adsjdhsajdh ajsd hjashd jsa hdasjhd jashdasd", enable=True
):
    example_function()
    time.sleep(1)
    example_function()

print(TimeTap.timeTap_get_str())
TimeTap.timeTap_print()
TimeTap.timeTap_reset()


with TimeTap.timeTap_log("Function 0", gpu=True):
    with TimeTap.timeTap_log(name="Function 1", gpu=True):
        time.sleep(0.1)


def worker_function():
    # Your code here
    with TimeTap.timeTap_log("Function B"):
        time.sleep(0.1)


@TimeTap.timeTap_log(name="Function A")
def thread_function():
    worker_function()
    time.sleep(0.1)  # Simulate some work


TimeTap.enable_timeTap()
threads = []
for _ in range(5):  # Create 5 threads
    thread = threading.Thread(target=thread_function)
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

TimeTap.timeTap_print()
TimeTap.timeTap_reset()
TimeTap.timeTap_print()
