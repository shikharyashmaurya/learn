"""
==============================================================================
DRILL 1.3: SCOPE RESOLUTION, CLOSURES & DECORATORS FROM SCRATCH
==============================================================================
Target: Master LEGB scoping, stateful closures with nonlocal, 2-tier and 3-tier
decorators, metadata preservation, and the closure late-binding trap.

Instructions:
1. Implement each function/decorator marked with TODO.
2. Run this file directly with Python:
      python drills/03_python_decorators.py
3. All assertions in run_tests() must PASS.
==============================================================================
"""

import functools
import time
from typing import Callable, Any, Tuple, Type, Dict


# ----------------------------------------------------------------------
# TASK 1: Stateful Closure with `nonlocal` (Moving Average Tracker)
# ----------------------------------------------------------------------
def make_moving_average() -> Callable[[float], float]:
    """
    In streaming LLM inference and agent telemetry, we need to track moving averages
    without the overhead of instantiating classes.

    Requirements:
    1. Return an inner function `calculate_avg(new_value: float) -> float`.
    2. Maintain `total_sum` and `count` in the enclosing scope.
    3. Use the `nonlocal` keyword to rebind these counters on each call.
    4. Return the running average: total_sum / count on each invocation.
    5. No global variables, no classes.
    """
    # TODO: Implement stateful closure with nonlocal
    total=0.0
    counter=0

    def calculate_avg(new_value):
        nonlocal total
        nonlocal counter

        counter+=1
        total+=new_value
        average=total/counter

        return average

    return calculate_avg



# ----------------------------------------------------------------------
# TASK 2: 2-Tier Function Decorator with Metadata Preservation
# ----------------------------------------------------------------------
def audit_agent_action(log_target: list) -> Callable:
    """
    A 2-tier decorator that logs tool invocations and execution status into `log_target`.

    Requirements:
    1. Decorate the target function so that whenever it is called:
       - Append a dict before/after call:
         {"func": func.__name__, "args": args, "result": result}
       - Return the original function's result.
    2. MUST preserve the original function's `__name__` and `__doc__`
       using `@functools.wraps(func)`.
    """
    def decorator(func: Callable) -> Callable:
        # TODO: Implement wrapper preserving metadata
        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            temp=func(*args,**kwargs)
            log_target.append({"func": func.__name__, "args": args, "result": temp})
            return temp
        return wrapper
    return decorator


# ----------------------------------------------------------------------
# TASK 3: 3-Tier Parameterized Decorator with Retries
# ----------------------------------------------------------------------
def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 0.01,
    backoff_factor: float = 2.0,
    target_exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """
    A 3-tier parameterized decorator used across API gateways to retry transient failures.

    Requirements:
    1. Outer tier: receives configuration parameters.
    2. Middle tier: receives the target function `func`.
    3. Inner tier: the wrapper accepting `*args, **kwargs`.
    4. Execution logic:
       - Attempt to run `func(*args, **kwargs)`.
       - If an exception listed in `target_exceptions` occurs:
         * If attempt < max_retries: sleep for `current_delay`, multiply delay by `backoff_factor`, and retry.
         * If attempt == max_retries: re-raise the exception.
       - Any exception NOT in `target_exceptions` MUST be raised immediately without retrying.
    5. Preserve `__name__` and `__doc__` with `@functools.wraps`.
    """
    # TODO: Implement 3-tier parameterized retry decorator
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            current_delay=initial_delay
            for attempt in range(1,max_retries+1):    
                try:
                    return func(*args,**kwargs)
                except target_exceptions as e:
                    if attempt==max_retries:
                        raise e
                    time.sleep(current_delay)
                    current_delay*=backoff_factor
            return func
        return wrapper
    return decorator


# ----------------------------------------------------------------------
# TASK 4: In-Memory Memoization Decorator
# ----------------------------------------------------------------------
def memoize(func: Callable) -> Callable:
    """
    Build a custom caching decorator from scratch (without using `functools.lru_cache`).

    Requirements:
    1. Store cache results in a dictionary enclosed within the decorator scope.
    2. Construct a hashable cache key from `args` and sorted `kwargs.items()`.
    3. If the key exists in cache, return the cached result immediately (cache hit).
    4. If the key is not in cache, call `func(*args, **kwargs)`, store in cache, and return it.
    5. Attach a `cache_info` method to the returned wrapper that returns:
       {"hits": hits_count, "misses": misses_count, "size": current_cache_size}
    6. Preserve function metadata with `@functools.wraps(func)`.
    """
    # TODO: Implement memoization decorator with cache_info stats
    # 1. State enclosed in the closure:
    cache = {}
    hits = 0
    misses = 0
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        nonlocal hits, misses
        # 2. Build hashable key:
        # args is a tuple (hashable).
        # kwargs is a dict (unhashable) -> converted to a sorted tuple of (key, value) pairs:
        key = (args, tuple(sorted(kwargs.items())))
        # 3. Cache Hit check:
        if key in cache:
            hits += 1
            return cache[key]
        # 4. Cache Miss: compute, cache, and return:
        misses += 1
        result = func(*args, **kwargs)
        cache[key] = result
        return result
    # 5. Helper function attached directly to the wrapper object (first-class function):
    def cache_info() -> Dict[str, int]:
        return {
            "hits": hits,
            "misses": misses,
            "size": len(cache)
        }
    wrapper.cache_info = cache_info
    return wrapper


# ----------------------------------------------------------------------
# TASK 5: The Late-Binding Closure Trap
# ----------------------------------------------------------------------
def create_multipliers_fixed() -> list:
    """
    The Classic Python Trap:
    ```python
    multipliers = [lambda x: x * i for i in range(5)]
    [m(2) for m in multipliers]  # Returns [8, 8, 8, 8, 8] instead of [0, 2, 4, 6, 8]!
    ```
    Why? Closures bind to variables in the enclosing scope by REFERENCE, not by value.
    When invoked, all lambdas look up `i`, which is now 4.

    Requirements:
    Fix this function to return a list of 5 multiplier functions such that:
    - multipliers[0](2) == 0
    - multipliers[1](2) == 2
    - multipliers[2](2) == 4
    - multipliers[3](2) == 6
    - multipliers[4](2) == 8
    Fix it using default argument binding: `lambda x, i=i: ...` OR an inner factory closure.
    """
    # TODO: Implement list of 5 closures binding `i` at creation time, not call time
    multipliers = [lambda x,i=i: x * i for i in range(5)]
    return multipliers


# ======================================================================
# TEST RUNNER & ASSERTIONS
# ======================================================================
def run_tests():
    print("Running Drill 1.3 tests...\n")

    # --- Test 1: Stateful Closure with nonlocal ---
    avg_tracker = make_moving_average()
    assert avg_tracker(10.0) == 10.0
    assert avg_tracker(20.0) == 15.0
    assert avg_tracker(30.0) == 20.0
    assert avg_tracker(40.0) == 25.0

    # Independent second instance verification
    tracker_2 = make_moving_average()
    assert tracker_2(100.0) == 100.0
    assert avg_tracker(50.0) == 30.0  # First tracker unchanged by second
    print("✅ Task 1 Passed: Stateful closure with nonlocal verified.")

    # --- Test 2: 2-Tier Decorator & Metadata Preservation ---
    audit_log = []

    @audit_agent_action(audit_log)
    def calculate_token_cost(tokens: int, model: str = "gemini-flash") -> float:
        """Calculate LLM cost based on token count."""
        return tokens * 0.0001

    res = calculate_token_cost(1000, model="gemini-pro")
    assert res == 0.1
    assert len(audit_log) == 1
    assert audit_log[0]["func"] == "calculate_token_cost"
    assert audit_log[0]["result"] == 0.1
    # Metadata preservation check:
    assert calculate_token_cost.__name__ == "calculate_token_cost"
    assert calculate_token_cost.__doc__ == "Calculate LLM cost based on token count."
    print("✅ Task 2 Passed: 2-tier decorator with functools.wraps metadata verified.")

    # --- Test 3: 3-Tier Parameterized Retry Decorator ---
    attempts_count = 0

    @retry_with_backoff(max_retries=3, initial_delay=0.001, backoff_factor=2.0, target_exceptions=(ValueError,))
    def flaky_api_call(succeed_on_attempt: int):
        """Flaky API call documentation."""
        nonlocal attempts_count
        attempts_count += 1
        if attempts_count < succeed_on_attempt:
            raise ValueError(f"Transient error on attempt {attempts_count}")
        return "SUCCESS"

    assert flaky_api_call(2) == "SUCCESS"
    assert attempts_count == 2
    assert flaky_api_call.__name__ == "flaky_api_call"
    assert flaky_api_call.__doc__ == "Flaky API call documentation."

    # Test re-raise on exceeding max_retries:
    attempts_count = 0
    exception_caught = False
    try:
        flaky_api_call(5)  # Needs 5 attempts, but max_retries is 3
    except ValueError:
        exception_caught = True
    assert exception_caught is True
    assert attempts_count == 3

    # Test immediate raise on untargeted exception:
    @retry_with_backoff(max_retries=3, initial_delay=0.001, target_exceptions=(ValueError,))
    def raise_type_error():
        raise TypeError("Not a ValueError")

    type_error_caught = False
    try:
        raise_type_error()
    except TypeError:
        type_error_caught = True
    assert type_error_caught is True
    print("✅ Task 3 Passed: 3-tier parameterized retry decorator verified.")

    # --- Test 4: Memoize Decorator with Cache Stats ---
    call_count = 0

    @memoize
    def expensive_lookup(query: str, top_k: int = 5) -> str:
        """Fetch search results."""
        nonlocal call_count
        call_count += 1
        return f"Results for {query} (k={top_k})"

    # Misses:
    r1 = expensive_lookup("rag_optimization", top_k=5)
    r2 = expensive_lookup("agent_routing", top_k=3)
    assert call_count == 2

    # Hits:
    r3 = expensive_lookup("rag_optimization", top_k=5)
    r4 = expensive_lookup("rag_optimization", top_k=5)
    assert call_count == 2  # No increase
    assert r1 == r3 == "Results for rag_optimization (k=5)"

    stats = expensive_lookup.cache_info()
    assert stats["hits"] == 2
    assert stats["misses"] == 2
    assert stats["size"] == 2
    assert expensive_lookup.__name__ == "expensive_lookup"
    print("✅ Task 4 Passed: In-memory memoize decorator with cache_info verified.")

    # --- Test 5: Late Binding Closure Trap ---
    fixed_multipliers = create_multipliers_fixed()
    assert len(fixed_multipliers) == 5
    results = [m(2) for m in fixed_multipliers]
    assert results == [0, 2, 4, 6, 8], f"Expected [0, 2, 4, 6, 8], got {results}"
    print("✅ Task 5 Passed: Late-binding closure trap resolved.")

    print("\n🎉 ALL DRILL 1.3 TESTS PASSED! Ready for Step 3: Interview Grilling.")


if __name__ == "__main__":
    run_tests()
