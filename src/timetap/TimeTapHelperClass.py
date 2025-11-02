from copy import deepcopy
from logging import warning
import time
from contextlib import contextmanager
from collections import defaultdict
import statistics
import threading
from threading import local

try:
    import torch
except ImportError:
    pass


class TimeTapHelperClass:
    """Singleton helper that tracks hierarchical timing metrics across threads.

    Provides thread-local stacks for nested timing contexts, a shared metrics
    store protected by a lock, and utilities to format and reset collected data.
    """

    _instance = None

    def __new__(cls: "TimeTapHelperClass") -> "TimeTapHelperClass":
        """
        Create or return the singleton instance.

        Ensures a single shared instance is used across the process, and that
        thread-local storage, a global lock, the metrics container, and related
        defaults are initialized exactly once.

        Returns:
            TimeTapHelperClass: the singleton instance.
        """
        if cls._instance is None:
            cls._instance = super(TimeTapHelperClass, cls).__new__(cls)
            cls._instance.thread_local = local()
            cls._instance.lock = threading.Lock()
            cls._instance.metrics = defaultdict(
                lambda: {"timings": [], "children": defaultdict(dict)}
            )
            cls._instance.max_depth = None
            cls._instance.min_width_func = 15
            cls._instance.max_width_func = 80
            cls._instance.have_printed_gpu_warning = False
            cls._instance.have_printed_enabled_warning = False
            cls._instance.enabled = True

            # Put any initialization here.
        return cls._instance

    def __init__(self):
        if not hasattr(self.thread_local, "initialized"):
            self.thread_local.current_path = []
            self.thread_local.initialized = True
        """
        Ensure the instance is ready for use.

        Calls internal initialization to set up any per-thread data structures
        required before the instance is used by the current thread.
        """

    def reset(self):
        """
        Clear all collected metrics and reset configuration.
        """
        with self.lock:
            self.metrics.clear()

    def __sync_cuda(self, gpu=False):
        if gpu:
            try:
                torch.cuda.synchronize()
            except NameError:
                if not self.have_printed_gpu_warning:
                    warning(
                        "torch not available, cannot synchronize GPU. Have you installed timetap[torch]?"
                    )
                self.have_printed_gpu_warning = True

    def log(self, name: str, enable=True, verbose=False, gpu=False):
        """
        Context manager-style generator that times a code block and records metrics.

        Intended to be used via the provided log context manager wrapper.
        Behavior:
          - Optionally synchronizes CUDA when gpu=True (if torch is available).
          - Appends `text` to the current thread-local nested path.
          - Measures elapsed wall-clock time for the enclosed block.
          - Optionally prints a verbose timing line.
          - Updates the shared hierarchical metrics store with the measured time.

        Parameters:
            text (str): A short label for this timing scope; used in the metric tree.
            enable (bool): If False, the timing is skipped and no metric is recorded.
            verbose (bool): If True, prints a human-readable timing line for the scope.
            gpu (bool): If True and torch is available, synchronizes CUDA before/after measurement.

        Yields:
            None: designed as a context manager generator (use with `with`).
        """
        # self.__ensure_initialized()  # Ensure initialization before each use
        self.thread_local.current_path.append(name)

        if not enable or not self.enabled:
            yield
        else:
            self.__sync_cuda(gpu=gpu)
            start = time.perf_counter()
            yield
            self.__sync_cuda(gpu=gpu)
            end = time.perf_counter()
            if verbose:
                print(
                    " -> ".join(self.thread_local.current_path), f"{end - start:.4f} s"
                )

            self.__update_metrics(end - start)

        self.thread_local.current_path.pop()

    def __update_metrics(self, elapsed):
        """
        Record an elapsed time into the metrics tree for the current thread path.

        Walks the thread-local `current_path` from root to leaf, creating nodes
        as necessary, and appends the elapsed time only to the final (leaf) node.
        The operation is performed while holding the instance lock to ensure
        thread-safe updates.
        """
        with self.lock:
            current = self.metrics
            for i, part in enumerate(self.thread_local.current_path):
                if part not in current:
                    current[part] = {"timings": [], "children": defaultdict(dict)}
                if i == (
                    len(self.thread_local.current_path) - 1
                ):  # Only add timing to the last function in the stack
                    current[part]["timings"].append(elapsed)
                current = current[part]["children"]

    def str_metrics(self, node=None, depth=0, path=[]):
        """
        Produce a formatted multi-line string representation of collected metrics.

        Traverses the hierarchical metrics tree and builds a readable table that
        includes run counts, total/median/average/min/max timings (in milliseconds)
        and a simple ASCII tree showing nesting. Designed for display in terminals

        Parameters:
            node (dict|None): Internal use. If None, rendering starts at the root.
            depth (int): Internal recursion depth counter.
            path (list): Internal path accumulator for recursion.

        Returns:
            str: The formatted metrics report.
        """
        result_str = ""
        if node is None:
            with self.lock:
                if not self.metrics:
                    return "No metrics to display."
                node = deepcopy(self.metrics)
            if self.max_depth is None:
                self.max_depth = 0
                for key in self.__flatten_dict(node):
                    adder_variable = 0
                    for k in key.split(" -> "):
                        self.max_depth = max(len(k) + adder_variable, self.max_depth)
                        adder_variable += 2
                        # due to the tree structure adding 2 spaces per depth
                self.max_depth = min(
                    max(self.max_depth, self.min_width_func), self.max_width_func
                )

            header = f"{'Function':<{self.max_depth}} {'Runs':>8} {'Total(ms)':>12} {'Median(ms)':>12} {'Avg(ms)':>12} {'Min(ms)':>12} {'Max(ms)':>12}\n"
            separator_bold = "\033[1m" + "-" * len(header) + "\033[0m\n"
            separator = "-" * len(header) + "\n"
            result_str = separator_bold + header + separator

        for idx, (text, data) in enumerate(
            sorted(
                node.items(),
                key=lambda item: (
                    statistics.median(item[1]["timings"]) if item[1]["timings"] else 0
                ),
                reverse=True,
            )
        ):

            current_path = path + [text]
            timings = data["timings"]
            count = len(timings)

            if count > 0:
                total_time = sum(timings) * 1000
                average_time = total_time / count
                median_time = statistics.median(timings) * 1000
                min_time = min(timings) * 1000
                max_time = max(timings) * 1000

                indent = ""
                if depth > 0:
                    if idx == len(node) - 1 and depth == 1:
                        indent += "└─"
                    else:
                        indent += "├─"
                    indent += "──" * (depth - 1)

                path_str = current_path[-1]
                func_name = indent + path_str
                if len(func_name) > self.max_depth:
                    func_name = func_name[: self.max_depth - 3] + "..."

                result_str += f"{func_name:<{self.max_depth}}\033[93m{count:>8d}\033[0m \033[92m{total_time:>12.1f}\033[0m \033[96m{median_time:>12.1f}\033[0m \033[94m{average_time:>12.1f}\033[0m \033[95m{min_time:>12.1f}\033[0m \033[91m{max_time:>12.1f}\033[0m\n"

            if data["children"]:
                result_str += self.str_metrics(
                    data["children"], depth + 1, current_path
                )

        if depth == 0:
            self.max_depth = None

        return result_str

    def __flatten_dict(self, d, parent_key="", sep=" -> ") -> dict:
        """
        Produce a flattened mapping of the hierarchical metrics tree.

        Recursively converts nested `children` structures into a single-level
        dict mapping joined paths (using `sep`) to their corresponding node data.
        Useful for computing layout parameters and performing global analyses.

        Parameters:
            d (dict): The hierarchical metrics dictionary (subtree).
            parent_key (str): Accumulated key prefix for recursion.
            sep (str): Separator used to join path components.

        Returns:
            dict: Flattened dictionary mapping 'A -> B -> C' -> node_data.
        """
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if "children" in v and v["children"]:
                items.extend(
                    self.__flatten_dict(v["children"], new_key, sep=sep).items()
                )
            else:
                items.append((new_key, v))
        return dict(items)

    def set_enabled(self, enabled=False):
        """
        Enable or disable timing measurements globally.

        When disabled, all subsequent log contexts become no-ops.
        """
        if (
            self.enabled != enabled
            and enabled is False
            and self.have_printed_enabled_warning is False
        ):
            warning("Disabling TimeTap timing measurements globally.")
            self.have_printed_enabled_warning = True
        self.enabled = enabled
