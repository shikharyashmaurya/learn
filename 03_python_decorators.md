# Drill 1.3: Step 1 Mental Models & Pointer Mechanics

## Topic: Scope Resolution (LEGB), Closures & Decorators from Scratch

---

### 1. Scope Resolution: The LEGB Hierarchy
When Python encounters an identifier, it searches 4 namespaces from inside out:

```
+-------------------------------------------------------------+
| Built-in (B): len, range, Exception, print                  |
|  +-------------------------------------------------------+  |
|  | Global (G): Module-level variables & imports          |  |
|  |  +-------------------------------------------------+  |  |
|  |  | Enclosing (E): Outer def function namespaces    |  |  |
|  |  |  +-------------------------------------------+  |  |  |
|  |  |  | Local (L): Inside current executing def  |  |  |  |
|  |  |  +-------------------------------------------+  |  |  |
|  |  +-------------------------------------------------+  |  |
|  +-------------------------------------------------------+  |
+-------------------------------------------------------------+
```

* **`global x`**: Forces assignments to write directly into module-level Global scope.
* **`nonlocal x`**: Binds assignments to the nearest **Enclosing** function scope (skipping Local, stopping before Global). Essential for stateful closures without class overhead.

---

### 2. Closures & CPython Cell Objects
A **closure** is a function that retains access to variables from its enclosing lexical scope even after that enclosing function has terminated and its stack frame is popped.

```
outer_func() executes and terminates:
[ STACK FRAME DESTROYED ]
            |
            v
HEAP PERSISTENCE:
make_worker() creates:
  inner_func -----------------> PyFunctionObject
                                   |
                                   +--> __closure__: ( <cell: id 0x55A>, )
                                                            |
                                                            v
                                                  cell_contents: tracked_state
```

* CPython captures enclosed variables using **`cell` objects**.
* You can inspect them directly: `fn.__closure__[0].cell_contents`.

---

### 3. Decorator Anatomy: 2-Tier vs 3-Tier

#### The Fundamental Reassignment Equation
The `@` syntax is syntactic sugar for wrapping a function call:
```python
@my_decorator
def calculate(): pass

# Exactly identical to:
calculate = my_decorator(calculate)
```

#### 2-Tier Decorator (No Arguments)
When a decorator takes no arguments, it needs 2 layers:
1. **Tier 1 (Decorator):** Receives the target function `func`.
2. **Tier 2 (Wrapper):** Accepts `*args, **kwargs` at runtime, runs pre/post logic, and returns the result.

#### 3-Tier Parameterized Decorator (With Arguments)
When a decorator takes configuration options (e.g. `@enforce_rate_limit(max_per_sec=5)`), it requires an outer factory tier:
```python
# @enforce_rate_limit(max_per_sec=5)
# Exactly identical to: action = enforce_rate_limit(max_per_sec=5)(action)

def enforce_rate_limit(max_per_sec: int):    # Tier 1 (Factory): Takes configuration
    def decorator(func):                     # Tier 2 (Decorator): Takes function
        @functools.wraps(func)
        def wrapper(*args, **kwargs):        # Tier 3 (Wrapper): Intercepts call
            # Rate limiting validation here...
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

---

### 4. Selective Exception Handling & Retry Mechanics
When building resilient wrappers (e.g. retrying transient database pings or network timeouts):

```
                   Call func(*args, **kwargs)
                               |
               +---------------+---------------+
               |                               |
            Success?                        Exception?
               |                               |
         return result           Is error in targeted_tuple?
                                               |
                                +--------------+--------------+
                                |                             |
                               YES                            NO
                                |                             |
                        Last attempt reached?          Bypasses except block;
                                |                      bubbles up immediately!
                         +------+------+
                         |             |
                        YES            NO
                         |             |
                     Re-raise!      Apply delay / backoff
                     (Give up)      Continue retry loop
```

* **Exception Filtering:** In Python, `except tuple_of_classes as err:` only intercepts exceptions matching that tuple. Any other exception type (e.g. `TypeError` when watching for `ConnectionError`) will **not** match the `except` clause and will immediately propagate outwards without entering the retry loop.
* **Retry Loop:** Loop through attempt counts. If an error is caught and attempts remain, wait/backoff and continue. Once the attempt limit is reached, re-raise the caught error (`raise err`).

---

### 5. Closure-Enclosed Cache & Functions as First-Class Objects
In Python, **functions are first-class objects**, meaning they can hold private state via closures and have custom attributes/methods attached directly to them.

```
       stateful_wrapper_factory(func)
                     |
                     +--> private_store = {}        (enclosed dict in closure)
                     +--> stats = {"calls": 0}      (enclosed mutable state)
                     |
                     +--> wrapper(*args, **kwargs)
                     |        |
                     |        +--> Lookup in private_store
                     |        +--> Compute & update store if missing
                     |
                     +--> wrapper.get_stats = lambda: stats  (Attribute attached to function!)
```

* **The Hashable Key Rule for Keyword Arguments:**
  In caching, `args` is a tuple (already hashable). However, `kwargs` is a `dict` (`TypeError: unhashable type: 'dict'`).
  To use arbitrary kwargs as part of a dictionary key, convert the dictionary into a sorted sequence of immutable pairs:
  ```python
  # dict is unhashable -> sorted tuple of pairs is hashable!
  hashable_kw = tuple(sorted(kwargs.items()))
  composite_key = (args, hashable_kw)
  ```
* **Attaching Custom Functions to a Function:**
  Because a function is an instance of `PyFunctionObject`, you can assign properties or helper methods directly to it:
  ```python
  wrapper.reset_state = reset_function
  wrapper.inspect_stats = get_stats_function
  ```
  Callers can then invoke `my_func.inspect_stats()` directly from outside.

---

### 6. The Late-Binding Closure Trap (Reference vs Value Capture)
Why does creating functions in a loop capture unexpected values?

```python
# Conceptual Problem:
greeters = [lambda name: f"{salutation}, {name}" for salutation in ["Hi", "Hello", "Hey"]]
# greeters[0]("Alice") -> "Hey, Alice" (NOT "Hi, Alice"!)
```

* **The Cause (Late Binding):** Closures look up enclosing variables by **name reference** at the time the inner function is *called*, not when it was defined. By the time any greeter is called, the loop has already finished, and `salutation` remains pointed at the last element (`"Hey"`).
* **The Solution (Definition-Time Binding):**
  Python default parameter values are evaluated **at function definition time**:
  ```python
  greeters = [lambda name, prefix=salutation: f"{prefix}, {name}" for salutation in ["Hi", "Hello", "Hey"]]
  # greeters[0]("Alice") -> "Hi, Alice"
  ```
  `prefix=salutation` freezes the current value of the loop variable into each function's local `__defaults__` tuple when that specific lambda is created.

---

### 7. Metadata Preservation via `@functools.wraps(func)`
When a decorator returns `wrapper`, Python's runtime inspects `wrapper` instead of the original function:
* Without wraps: `fn.__name__` becomes `"wrapper"`, `fn.__doc__` becomes `None`, and type annotations are lost.
* With `@functools.wraps(func)`: CPython copies `__name__`, `__doc__`, `__module__`, `__annotations__`, and `__qualname__` from `func` to `wrapper`, preserving reflection, API documentation, and debugger stack traces.
