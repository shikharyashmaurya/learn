# Drill 1.3: Step 3 Interview Grilling & Assessment

* **Topic:** Scope Resolution (LEGB), Closures & Decorators from Scratch
* **Grill Attempt:** 1
* **Evaluation Verdict:** `NEEDS_REMEDIATION` (Gaps identified in `UnboundLocalError`/`LOAD_FAST` bytecode, `nonlocal` compile-time `SyntaxError`, 3-tier decorator desugaring function passing, and nested unhashable cache inputs).
* **Next Action:** Step 3 Attempt 2 Re-Grill.

---

## Question 1: The LEGB Rule, Symbol Tables & `UnboundLocalError`

### Full Question
```python
x = 10

def compute():
    print(x)
    x = 20

compute()
```
* **1.1:** What happens when `compute()` is called? What exact exception is raised, and on which line?
* **1.2:** Under the hood, why doesn't Python print `10` from the global scope and then reassign `x` locally? Explain how Python's compiler analyzes scope at compile time (mentioning `LOAD_FAST` vs `LOAD_GLOBAL` / local symbol table).
* **1.3:** If we have three levels of nested functions (`outer` -> `middle` -> `inner`), how does `nonlocal x` resolve? What happens if `x` is only defined in the global scope (does `nonlocal` fall back to global or raise a SyntaxError)?

### Candidate's Response (Attempt 1)
> *"1.1 - it gives error, variable x not found, on line print(x)*  
> *1.2 - first python check we have x included in function so it not look outside but during print it not find value so raise error not sure*  
> *1.3 - how does nonlocal x resolve? question unclear ask again. second part - i think it is asking we define nonlocal x but it is not in enclosure and in global - in case i think it will throw same error variable x not found"*

### Evaluator Assessment & Gap Analysis
* **Status:** ❌ **NEEDS REMEDIATION.**
* **Strengths:**
  * **1.1:** Correctly identified the failure line (`print(x)`).
  * **1.2:** Correct high-level intuition that Python detects `x` is inside the function and therefore doesn't look outside.
* **Gaps Identified:**
  * **1.1 (Exact Exception):** It is **not** "variable x not found" (`NameError`). The exact exception is:
    `UnboundLocalError: local variable 'x' referenced before assignment`.
  * **1.2 (Compiler / Bytecode Mechanism):** Needs senior-level CPython compilation clarity: `LOAD_FAST` vs `LOAD_GLOBAL` and symbol table construction.
  * **1.3 (`nonlocal` Mechanics):** Missed how `nonlocal` resolves through nested scopes, and thought missing enclosing `x` throws "variable not found", whereas CPython raises a compile-time `SyntaxError: no binding for nonlocal 'x' found`.

### Expected Senior Answer & CPython Internals

#### 1.1 Exact Exception & Line
* The exception is raised on line `print(x)`.
* Exact Exception: `UnboundLocalError: local variable 'x' referenced before assignment`.
* Note: `NameError` occurs when a variable is not found in *any* scope. `UnboundLocalError` is a subclass of `NameError` that specifically occurs when Python knows a variable is local to the current scope, but its local slot has not been assigned a value yet.

#### 1.2 CPython Compiler Mechanics: Symbol Table & Bytecode
* **Compile-Time Symbol Table:** Before executing any bytecode, CPython parses the code into an AST and runs a symbol table analysis pass (`symtable.c`).
* **The Rule:** If a variable is assigned to anywhere within a function body (e.g., `x = 20`), and has **not** been explicitly declared `global` or `nonlocal`, CPython marks `x` as **strictly local** to that function for the entire function's lifetime.
* **Bytecode Emission:**
  * Because `x` is marked local, the compiler generates the opcode `LOAD_FAST` (which indexes directly into the stack frame's fixed-size local variable array `fastlocals`), instead of emitting `LOAD_GLOBAL` or `LOAD_DEREF`.
  * When `print(x)` runs, CPython executes `LOAD_FAST` for `x`.
  * At that point, the local slot for `x` contains `NULL` (uninitialized). CPython checks if the slot is `NULL` and immediately raises `UnboundLocalError`. It **never** dynamically falls back to enclosing or global scopes at runtime.

#### 1.3 `nonlocal` Scope Resolution & Global Failure
* **Nested Resolution:** In nested functions (`outer` -> `middle` -> `inner`), declaring `nonlocal x` inside `inner` searches the enclosing namespaces **from nearest to farthest**:
  1. Searches `middle` scope first. If found, it binds to `middle`'s `x`.
  2. If not found in `middle`, it searches `outer`. If found, it binds to `outer`'s `x`.
  3. It binds to the **first (nearest)** enclosing function scope that defines `x`.
* **When `x` is only in Global scope:**
  * `nonlocal` **never** falls back to global or built-in scope.
  * If `x` exists only in the global scope (or nowhere at all), CPython raises a **compile-time `SyntaxError`**:
    `SyntaxError: no binding for nonlocal 'x' found`.
  * It fails before any code even runs!

### Revision Guide Pointer
* 📖 See **[revision/PYTHON_REVISION_GUIDE.md](file:///home/shikhar/Downloads/learn/revision/PYTHON_REVISION_GUIDE.md)** -> **Section 4.1 (Lines 720–753)**.

---

## Question 2: Closure Internals, `cell` Objects & The Late-Binding Trap

### Full Question
* **2.1:** When an outer function finishes execution, its stack frame is popped. How does CPython keep captured variables alive on the heap? What is a `cell` object, and which dunder attribute on the inner function stores it?
* **2.2:** Why does `multipliers = [lambda x: x * i for i in range(3)]` cause all functions to evaluate using `i = 2`? Explain the difference between **definition-time** vs **call-time** variable lookup in closures.
* **2.3:** In `lambda x, i=i: x * i`, why does this fix the bug? When does Python evaluate default parameter values, and which function attribute stores them?

### Candidate's Response (Attempt 1)
> *"2.1 - it sees that value is still referenced so not remove it ,it get stored in the inner function closure values, inner_function_name__closure__ fetched by inner_function_name__closure__[0].cell_contents*  
> *2.2- because it lloks at last value of i ,definition time are make at starting compile time and later when called*  
> *2.3- it stores value at creation time, fun_name.__defaults__ ,__kwdefaults__"*

### Evaluator Assessment & Gap Analysis
* **Status:** 🟡 **PARTIALLY PASSED (Solid intuition on 2.1 & 2.3; refine 2.2).**
* **Strengths:**
  * **2.1:** Accurately identified that enclosed variables persist on the heap via `__closure__` and are retrieved via `.cell_contents`.
  * **2.3:** Spot on! Correctly noted that default argument evaluation happens at creation time and is stored in `__defaults__` / `__kwdefaults__`.
* **Gaps Identified:**
  * **2.2 (Reference Binding vs Value Snapshot):** The explanation of definition-time vs call-time was slightly vague ("definition time are make at starting compile time and later when called"). Needed explicit articulation that closures bind to the variable's *name/cell reference*, not its current value at loop iteration time.

### Expected Senior Answer & CPython Internals

#### 2.1 Stack Frame Deallocation & Heap `cell` Objects
* When the outer function returns, its call stack frame (`PyFrameObject`) is deallocated and popped off the call stack.
* However, any variable marked as free/enclosed is not allocated on the stack; CPython allocates a **`PyCellObject`** on the **heap**.
* The cell object acts as an indirection pointer to the actual Python object on the heap.
* When the inner function object (`PyFunctionObject`) is created, CPython assigns a tuple of these cell objects to the function's **`__closure__`** attribute.
* The inner function holds an incremented reference count to each cell object, preventing garbage collection. At runtime, the value is read from `func.__closure__[idx].cell_contents`.

#### 2.2 Late-Binding Mechanics (Reference vs Value Capture)
* In Python, closures look up free variables **by name reference at call time**, not by value snapshot at definition time.
* When `[lambda x: x * i for i in range(3)]` is executed, all 3 lambdas are created sharing a reference to the **exact same cell object** representing the loop variable `i`.
* During the list comprehension, `i` is updated in-place in that cell: $0 \to 1 \to 2$.
* When any of the lambdas are subsequently called (`m(2)`), the bytecode executes `LOAD_DEREF` for `i`, which reads whatever value happens to be in that shared cell at that exact moment. Since the loop has completed, the cell contains `2`.

#### 2.3 The Default Argument Fix (`i=i`) & `__defaults__`
* In Python, default parameter expressions (`def f(x, i=i): ...`) are evaluated **once at function definition time**, not when the function is called.
* For each iteration of the loop, the current value of `i` ($0, 1, 2$) is evaluated and placed into that specific function object's **`__defaults__`** tuple (e.g. `(0,)`, `(1,)`, `(2,)`).
* Inside the lambda, `i` is now treated as a **local parameter** rather than an enclosed free variable. When called as `m(2)`, it defaults to the value frozen in its `__defaults__`.

---

## Question 3: Decorator Desugaring, Metadata & Agent Production Traps

### Full Question
* **3.1:** Write the exact mathematical/syntactic equivalent assignment for this parameterized decorator without using the `@` symbol:
  ```python
  @retry_with_backoff(max_retries=3, backoff_factor=2.0)
  def fetch_agent_plan(goal: str):
      ...
  ```
* **3.2:** In production agent frameworks (like FastAPI route handlers, LangGraph tool registries, or OpenAI/Anthropic function calling), what breaks catastrophically if your decorator forgets `@functools.wraps(func)`?
* **3.3:** In building `memoize`, we used `tuple(sorted(kwargs.items()))`. Why can't a `dict` be used directly as a cache key? If a caller passes `fetch_agent_plan(goal="deploy", context={"nodes": [1, 2]})`, what error will occur in your cache, and how do production memoization layers handle unhashable arguments?

### Candidate's Response (Attempt 1)
> *"3.1 - fetch_agent_plan = retry_with_backoff(max_retries=3, backoff_factor=2.0)(fetch_agent_plan(goal)*  
> *3.2- it will forget all metadata like name ,doc etc*  
> *3.3- it is not hashable, valueeror, not sure"*

### Evaluator Assessment & Gap Analysis
* **Status:** ❌ **NEEDS REMEDIATION.**
* **Strengths:**
  * **3.2:** Correctly identified that `__name__` and `__doc__` are lost.
  * **3.3:** Correctly identified that `dict` is unhashable.
* **Gaps Identified:**
  * **3.1 (Syntactic Desugaring):** Candidate wrote `...(fetch_agent_plan(goal))`. Calling `fetch_agent_plan(goal)` inside the decorator assignment is a critical syntax/conceptual mistake. Decorators take the **function object** (`fetch_agent_plan`), NOT the result of calling the function!
  * **3.2 (Production Framework Failure):** Missing the catastrophic failure mechanism in LLM tool calling and FastAPI: reflection via `inspect.signature()` and `__annotations__`.
  * **3.3 (Unhashable Inputs & Handling):** Candidate was "not sure" about nested unhashable structures (e.g. dict containing a list) and production solutions.

### Expected Senior Answer & CPython Internals

#### 3.1 Exact Parameterized Desugaring
```python
# The @ syntax:
# @retry_with_backoff(max_retries=3, backoff_factor=2.0)
# def fetch_agent_plan(goal: str): ...

# IS EXACTLY EQUIVALENT TO:
fetch_agent_plan = retry_with_backoff(max_retries=3, backoff_factor=2.0)(fetch_agent_plan)
```
* Step 1: `retry_with_backoff(max_retries=3, backoff_factor=2.0)` is evaluated first. It returns the middle-tier `decorator` function.
* Step 2: The returned `decorator` is called with the **function object** `fetch_agent_plan`: `decorator(fetch_agent_plan)`.
* Step 3: It returns `wrapper`, which is rebound to the name `fetch_agent_plan`.
* ⚠️ **Do NOT pass `fetch_agent_plan(goal)`!** That would execute the function before decorating it and pass its return value to the decorator.

#### 3.2 Catastrophic Production Failures without `@functools.wraps`
When `@functools.wraps(func)` is omitted:
1. **LangGraph & LLM Tool Calling:** Agent frameworks inspect `func.__doc__` to construct the tool description prompt for the LLM, and inspect `func.__annotations__` / `inspect.signature(func)` to generate the JSON Schema for tool calling. Without `wraps`, the LLM receives `wrapper(*args, **kwargs)` with `__doc__ = None`, stripping all parameter types and descriptions. The LLM cannot figure out how to call the tool.
2. **FastAPI Route Handlers:** FastAPI inspects function signatures and type annotations to generate OpenAPI documentation and validate Pydantic request bodies. With an unwrapped `wrapper(*args, **kwargs)`, FastAPI fails to detect path/query parameters, breaking API generation.
3. **Debugging / Stack Traces:** Stack traces display `wrapper` instead of the original function name, complicating telemetry and APM logging.

#### 3.3 The Unhashable Argument Problem & Production Solutions
* **Why Dict cannot be a key:** `dict` is mutable and lacks a `__hash__` method (`TypeError: unhashable type: 'dict'`).
* **The Nested Trap:** `tuple(sorted(kwargs.items()))` converts the top-level kwargs dict into a tuple of pairs: `(('context', {'nodes': [1, 2]}),)`. However, the value `{'nodes': [1, 2]}` is **still a dict containing a list**. When Python attempts to compute `hash(key)`, it recursively hashes tuple elements and raises:
  `TypeError: unhashable type: 'dict'` (or `'list'`).
* **How Production Memoization Handles Unhashable Arguments:**
  1. **Selective Bypass:** If an argument is unhashable, skip the cache lookup, run the function, and return the result without caching (or log a warning).
  2. **Deterministic Serialization (e.g. JSON/Pickle hashing):** Serialize arguments to a canonical string representation using `json.dumps(obj, sort_keys=True)` or `pickle` and compute a SHA-256 hash as the cache key.
  3. **Recursive Freezing:** Recursively transform mutable structures (lists $\to$ tuples, dicts $\to$ sorted tuples or `frozendict`).
  4. **Strict Enforcement (like `functools.lru_cache`):** Explicitly raise `TypeError: unhashable type` and require callers to pass immutable types.

---

## Attempt 1 Verdict: ❌ NEEDS REMEDIATION
The candidate demonstrated strong foundational mental models for closures and defaults, but showed gaps in CPython bytecode scope compilation (`LOAD_FAST` vs `LOAD_GLOBAL`), `nonlocal` compile-time `SyntaxError`, decorator desugaring mechanics, and nested cache serialization.

**Proceeding immediately to Step 3: Attempt 2 (Targeted Re-Grill).**
