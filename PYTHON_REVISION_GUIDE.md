# ==============================================================================
#                 SENIOR PYTHON INTERVIEW REVISION GUIDE
# ==============================================================================
# Focus: Complete Answers to Every Interview Question, Syntax Rules & Internals
# Target: AI / ML Engineer & Senior Backend (No assumed knowledge, full syntax clarity)
# ==============================================================================

## TABLE OF CONTENTS
1. Master Q&A: Direct Answers to the Top 15 Python Interview Questions
2. Syntax Deep-Dive: Slicing, Comprehensions, Unpacking & Arguments
3. Module 1: The Python Data Model, Mutability & Memory Internals
4. Module 2: Scoping, Functional Mechanics & Metaprogramming
5. Module 3: Object-Oriented Architecture, Dunders & Internals
6. Module 4: Concurrency (GIL, Threading, Multiprocessing, Asyncio)
7. Module 5: High-Frequency Live-Coding Implementations (LRU, Rate Limiter, Streaming)
8. Module 6: Edge-Cases, Syntax Gotchas & "What Does This Output?"

---

# 1. MASTER Q&A: DIRECT ANSWERS TO TOP 15 INTERVIEW QUESTIONS

### Q1: Is Python pass-by-value or pass-by-reference?
* **Common Misunderstanding:** Thinking primitive types (int, float) are pass-by-value and collections (list, dict) are pass-by-reference.
* **The Direct Interview Answer:**
  > "Python is neither. Python is **Call-by-Object-Reference** (also called **Pass-by-Assignment**). Every variable is a reference (pointer) to a heap object. When a function is called, the argument identifiers are assigned a *copy of the reference*. If you mutate the object through that reference in-place (e.g., `list.append()`), the caller sees the change. But if you reassign the variable (e.g., `x = 10` or `lst = [1, 2]`), you simply rebind the local name to a new object; the caller's reference remains completely unchanged."
* **Code Proof:**
```python
def rebind_vs_mutate(lst, num):
    lst.append(99)  # Mutating in-place: caller sees this!
    num += 10       # Rebinding local name 'num' to a new int: caller does NOT see this!
    lst = [1000]    # Rebinding local name 'lst' to a new list: caller does NOT see this!

my_list = [1, 2]
my_num = 5
rebind_vs_mutate(my_list, my_num)
print(my_list)  # Output: [1, 2, 99]
print(my_num)   # Output: 5
```

---

### Q2: What is the mutable default argument trap, and how do you fix it?
* **Common Misunderstanding:** Assuming default arguments are created fresh each time the function is called.
* **The Direct Interview Answer:**
  > "In Python, default arguments are evaluated **once at function definition time**, when the module is compiled/loaded, not at runtime when the function is called. Therefore, if the default argument is a mutable object like a list or dictionary, all subsequent invocations that omit that parameter share the exact same object in memory. The fix is to use `None` as the sentinel default and instantiate a fresh container inside the function body."
* **Code Proof:**
```python
# ❌ BUGGY: Default list is created once in memory
def add_item_buggy(item, container=[]):
    container.append(item)
    return container

print(add_item_buggy("A"))  # ['A']
print(add_item_buggy("B"))  # ['A', 'B'] -> Shared state bug!

# ✅ CORRECT IDIOM:
def add_item_correct(item, container=None):
    if container is None:
        container = []  # Created anew on every execution where container is omitted
    container.append(item)
    return container

print(add_item_correct("A"))  # ['A']
print(add_item_correct("B"))  # ['B'] -> Isolated!
```

* **Under the Hood (CPython Internals & Design Rationale):**
  1. **Where Defaults are Stored:** Positional defaults are bound to the function object's `__defaults__` tuple (`add_item_buggy.__defaults__`). Keyword-only defaults are stored in `__kwdefaults__` (a dict). Mutating the default container directly modifies the object inside `func.__defaults__`!
  2. **Why Python Evaluates at Definition Time:**
     * **Performance:** Python functions are first-class callable objects created once. Evaluating defaults dynamically on every invocation would introduce CPU overhead into every function call.
     * **Deterministic Scoping:** Default expressions are bound within the enclosing lexical scope where the function was authored, preventing call-site namespace ambiguities.

---

### Q3: What is the difference between `is` and `==`?
* **Common Misunderstanding:** Believing `is` and `==` are interchangeable for numbers and strings.
* **The Direct Interview Answer:**
  > "`==` tests for **value equality** by invoking the `__eq__()` dunder method. `is` tests for **object identity** by verifying whether both pointers point to the exact same memory address (`id(a) == id(b)`). While `x == y` is true if their contents match, `x is y` is only true if they are the exact same instance in the heap. CPython caches small integers from -5 to 256 and interns small strings, which can make `is` appear to work for numbers, but relying on `is` for value comparison is a critical bug."
* **Code Proof:**
```python
a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)  # True  (same values inside)
print(a is b)  # False (different heap locations)

# CPython integer caching optimization:
x = 256
y = 256
print(x is y)  # True  (CPython maintains a singleton array for -5 to 256)

x = 257
y = 257
print(x is y)  # False in interactive shell (allocated as separate heap objects)
```

---

### Q4: What is the Global Interpreter Lock (GIL), and how do you achieve true CPU parallelism?
* **Common Misunderstanding:** Believing multithreading in Python uses multiple CPU cores for CPU-heavy tasks.
* **The Direct Interview Answer:**
  > "The GIL is a mutual exclusion lock used by CPython to ensure that only one native thread executes Python bytecode at any given moment. It exists because CPython's internal memory management uses reference counting, which is not thread-safe; without the GIL, concurrent access would corrupt reference counters. 
  > For **I/O-bound tasks** (network requests, disk access), the GIL is released during system calls, making multithreading or asyncio effective.
  > For **CPU-bound tasks** (mathematical operations, image processing, model training), multithreading cannot use multiple cores because threads contend for the GIL. To achieve true parallelism, we use the `multiprocessing` module (separate processes with independent Python interpreters and heaps) or leverage C-extension libraries like NumPy and PyTorch which release the GIL during heavy computation. Note that Python 3.13 introduces experimental free-threaded CPython (PEP 703) to disable the GIL."
* **Code Proof:**
```python
# CPU-bound tasks should use ProcessPoolExecutor, NOT ThreadPoolExecutor:
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import time

def cpu_heavy_task(n):
    return sum(i * i for i in range(n))

# ProcessPoolExecutor achieves TRUE multi-core parallelism:
# with ProcessPoolExecutor() as executor:
#     results = list(executor.map(cpu_heavy_task, [10_000_000, 10_000_000]))
```

---

### Q5: What is the difference between shallow copy and deep copy?
* **Common Misunderstanding:** Assuming `list.copy()` or slicing `lst[:]` creates a completely independent copy of nested lists.
* **The Direct Interview Answer:**
  > "A **shallow copy** constructs a new compound collection, but populates it with references to the child objects found in the original. If the original contains nested mutable objects (like a list of lists or dict of dicts), modifying a child object in the copy will modify the original.
  > A **deep copy** recursively duplicates all nested objects found in the original, ensuring complete memory isolation."
* **Code Proof:**
```python
import copy

original = [[1, 2], [3, 4]]

# Shallow copy via:
# 1. slice: original[:]
# 2. constructor: list(original)
# 3. unpacking: [*original]
# 4. copy.copy(original)
shallow = copy.copy(original)
shallow[0].append(99)
print(original)  # [[1, 2, 99], [3, 4]] -> ORIGINAL MUTATED!

# Deep copy via copy.deepcopy()
deep = copy.deepcopy(original)
deep[0].append(1000)
print(original)  # [[1, 2, 99], [3, 4]] -> ORIGINAL UNTOUCHED!
print(deep)      # [[1, 2, 99, 1000], [3, 4]]

# Cycle-Safety in Cyclic Graphs (Agentic DAGs / Knowledge Graphs):
# deepcopy does NOT cause RecursionError on cycles (e.g., node['self'] = node).
# Internally, copy.deepcopy maintains an internal `memo` dictionary:
#   memo = {id(obj): cloned_obj}
# Before copying any object, deepcopy checks `if id(obj) in memo: return memo[id(obj)]`.
# This detects cycles in O(1) time and preserves identical graph topologies.
```

---

### Q6: Why does `[lambda: i for i in range(5)]` return all 4s, and how do you fix it?
* **Common Misunderstanding:** Believing each lambda captures the value of `i` at the moment of creation.
* **The Direct Interview Answer:**
  > "This is known as the **late-binding closure trap**. In Python, closures look up free variables dynamically in the enclosing scope when the function is *invoked*, not when it is *defined*. When the lambdas are later called, the loop has already completed, and the variable `i` in the enclosing scope equals `4`.
  > The fix is to use a default argument: `lambda i=i: ...`. Default arguments are evaluated at definition time, effectively freezing a local copy of `i` inside each lambda's scope."
* **Code Proof:**
```python
# ❌ TRAP:
funcs = [lambda: i for i in range(5)]
print([f() for f in funcs])  # [4, 4, 4, 4, 4]

# ✅ FIX (Default argument binding):
fixed_funcs = [lambda i=i: i for i in range(5)]
print([f() for f in fixed_funcs])  # [0, 1, 2, 3, 4]
```

---

### Q7: What is the difference between an Iterable, an Iterator, and a Generator?
* **Common Misunderstanding:** Using the terms interchangeably.
* **The Direct Interview Answer:**
  > "1. An **Iterable** is any object that can return an iterator. It implements the `__iter__()` method (e.g., `list`, `str`, `dict`).
  > 2. An **Iterator** is an object with state that produces the next value in sequence. It implements both `__iter__()` (returns itself) and `__next__()` (returns the next item or raises `StopIteration`).
  > 3. A **Generator** is a special function that simplifies writing iterators using the `yield` statement. When called, it does not execute immediately; it returns a generator object that lazily produces values one at a time on-demand, consuming $O(1)$ memory."
* **Code Proof:**
```python
# 1. Custom Iterator:
class StepCounter:
    def __init__(self, limit):
        self.limit = limit
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.limit:
            raise StopIteration
        val = self.current
        self.current += 1
        return val

# 2. Equivalent Generator Function:
def step_generator(limit):
    for i in range(limit):
        yield i  # Yields value, suspends execution state, consumes O(1) memory
```

---

### Q8: What does `@functools.wraps` do, and what happens if you omit it?
* **Common Misunderstanding:** Thinking decorators work identically with or without `@functools.wraps`.
* **The Direct Interview Answer:**
  > "A decorator wraps a function in an inner function. Without `@functools.wraps`, the decorated function loses its identity: its `__name__`, `__doc__`, `__annotations__`, and `__module__` are overwritten by those of the inner wrapper function. This breaks docstring generation, debugging tools, logging, and inspection frameworks like FastAPI or Pydantic. `@functools.wraps(func)` copies the original function's metadata onto the wrapper."
* **Code Proof:**
```python
import functools

# ❌ WITHOUT wraps:
def bad_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@bad_decorator
def greet(name: str) -> str:
    """Greets the user."""
    return f"Hello {name}"

print(greet.__name__)  # 'wrapper' (Lost!)
print(greet.__doc__)   # None (Lost!)

# ✅ WITH wraps:
def good_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@good_decorator
def greet_fixed(name: str) -> str:
    """Greets the user."""
    return f"Hello {name}"

print(greet_fixed.__name__)  # 'greet_fixed' (Preserved!)
print(greet_fixed.__doc__)   # 'Greets the user.' (Preserved!)
```

---

### Q9: How does Python's Garbage Collection work?
* **Common Misunderstanding:** Believing Python only uses a mark-and-sweep garbage collector like Java.
* **The Direct Interview Answer:**
  > "CPython's primary memory management system is **Reference Counting**. Every object has an internal counter (`ob_refcnt`). When an object's reference count drops to zero, its memory is deallocated immediately.
  > Because reference counting cannot detect **circular references** (e.g., Object A references Object B and Object B references Object A, keeping ref counts at 1 even when unreachable), CPython runs a secondary **Generational Cyclic Garbage Collector**. This collector tracks objects in three generations (Gen 0, 1, and 2), checking younger generations frequently and older ones less often, detecting unreachable cycles and freeing their memory."
* **Code Proof:**
```python
import sys
import gc

a = [1, 2, 3]
print(sys.getrefcount(a))  # 2 (a + argument to getrefcount)

# Creating a reference cycle:
class Node:
    def __init__(self):
        self.partner = None

n1 = Node()
n2 = Node()
n1.partner = n2
n2.partner = n1  # Circular reference!

del n1
del n2  # Ref counts are still 1! Reference counting cannot free them.

# Cyclic GC detects and cleans them up:
collected = gc.collect()
print(f"Cyclic objects collected: {collected}")
```

---

### Q10: Why can't lists or dictionaries be dictionary keys or set elements?
* **Common Misunderstanding:** Assuming it is just an arbitrary rule.
* **The Direct Interview Answer:**
  > "Dictionary keys and set elements must be **hashable**. An object is hashable if its hash value never changes during its lifetime (`__hash__`) and it can be compared for equality (`__eq__`). 
  > Lists and dictionaries are mutable. If a mutable object were allowed as a dictionary key, mutating it after insertion would change its hash code. As a result, the dictionary would search the wrong hash bucket on subsequent lookups, corrupting the hash table. Therefore, Python makes mutable built-ins unhashable, raising a `TypeError: unhashable type: 'list'`."
* **Code Proof:**
```python
# ❌ TypeError: unhashable type: 'list'
# bad_dict = {[1, 2]: "value"}

# ✅ Use an immutable tuple instead:
good_dict = {(1, 2): "value"}
print(good_dict[(1, 2)])  # "value"
```

---

### Q11: What is the difference between `__new__` and `__init__`?
* **Common Misunderstanding:** Thinking `__init__` is the constructor that creates the object.
* **The Direct Interview Answer:**
  > "`__new__` is the actual **constructor** (allocator); it is a static method that allocates memory and returns a new instance of the class. 
  > `__init__` is the **initializer**; it receives the instance created by `__new__` and sets up attributes. 
  > `__new__` runs first. We override `__new__` when implementing Singletons, customizing subclassing of immutable types (like `int` or `tuple`), or writing metaclasses."
* **Code Proof:**
```python
class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # Allocate new instance via base object
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, val):
        self.val = val

s1 = Singleton(10)
s2 = Singleton(20)
print(s1 is s2)   # True (Same instance)
print(s1.val)     # 20 (Both point to the same object)
```

---

### Q12: How does Method Resolution Order (MRO) work in multiple inheritance?
* **Common Misunderstanding:** Thinking Python simply searches parent classes left-to-right depth-first.
* **The Direct Interview Answer:**
  > "Python uses the **C3 Linearization Algorithm** to determine MRO. It guarantees two properties:
  > 1. Children precede their parents.
  > 2. The order of appearance of parents in the class header is preserved.
  > In diamond inheritance hierarchies (where class `D(B, C)` inherits from `B` and `C`, both inheriting from `A`), C3 ensures common ancestors like `A` are visited only *after* all their subclasses are traversed: `D -> B -> C -> A -> object`. We can inspect the order using `ClassName.__mro__`."
* **Code Proof:**
```python
class A:
    def greet(self): return "A"

class B(A):
    def greet(self): return "B"

class C(A):
    def greet(self): return "C"

class D(B, C):
    pass

print([cls.__name__ for cls in D.__mro__])
# Output: ['D', 'B', 'C', 'A', 'object']
```

---

### Q13: What does `__slots__` do, and what are its trade-offs?
* **Common Misunderstanding:** Thinking `__slots__` is a security feature to prevent adding attributes.
* **The Direct Interview Answer:**
  > "`__slots__` is a **memory optimization**. By default, Python stores instance attributes in a dynamic dictionary `__dict__`, which incurs ~150 bytes of overhead per instance. Specifying `__slots__ = ('x', 'y')` tells Python to allocate a fixed-size array of pointers instead of a dictionary. This saves 60-70% memory when instantiating millions of objects (e.g., graph nodes, dataset tokens).
  > **Trade-offs:** You cannot dynamically attach new arbitrary attributes at runtime, and multiple inheritance of slotted classes requires careful design."
* **Code Proof:**
```python
class RegularPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class SlottedPoint:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = SlottedPoint(1, 2)
# p.z = 10  # Raises AttributeError: 'SlottedPoint' object has no attribute 'z'
```

---

### Q14: How does Asyncio differ from Multithreading?
* **Common Misunderstanding:** Thinking `async/await` runs code across multiple threads.
* **The Direct Interview Answer:**
  > "Multithreading uses **preemptive multitasking** managed by the OS kernel; the OS can interrupt and switch threads at any instruction, which introduces race conditions and requires mutex locks.
  > Asyncio uses **cooperative multitasking** running on a **single thread**. An event loop manages tasks. A task only yields control when it explicitly hits an `await` expression on an I/O operation. Because context switching only happens at explicit `await` points, there are no thread-switch race conditions on simple operations, and memory overhead is negligible (thousands of coroutines consume far less memory than thousands of OS threads)."
* **Code Proof:**
```python
import asyncio

async def fetch_item(item_id):
    # Explicit yield point: yields control back to event loop
    await asyncio.sleep(0.01)
    return f"item_{item_id}"

async def main():
    # Concurrently schedules 1000 tasks on a single thread
    tasks = [fetch_item(i) for i in range(1000)]
    results = await asyncio.gather(*tasks)
    print(f"Fetched {len(results)} items cooperatively.")

# asyncio.run(main())
```

---

### Q15: What happens when you execute `a = ([1, 2], 3); a[0] += [4]`?
* **Common Misunderstanding:** Assuming it either cleanly modifies the list OR raises an error without changing anything.
* **The Direct Interview Answer:**
  > "It does **both**: it raises a `TypeError: 'tuple' object does not support item assignment`, **AND** it successfully modifies the list inside the tuple to `[1, 2, 4]`!
  > **Why?** The `+=` operator performs two steps:
  > 1. It invokes `__iadd__()` on the object `a[0]`. Since lists are mutable, `__iadd__` mutates the list in-place by extending it with `[4]`.
  > 2. It attempts to assign the result back to `a[0]` (`a[0] = mutated_list`). Because `a` is a tuple and tuples are immutable, the assignment step raises `TypeError`. But step 1 already completed!"
* **Code Proof:**
```python
a = ([1, 2], 3)
try:
    a[0] += [4]
except TypeError as e:
    print(f"Error caught: {e}")

print("State of tuple 'a':", a)
# Output:
# Error caught: 'tuple' object does not support item assignment
# State of tuple 'a': ([1, 2, 4], 3)
```

---

# 2. SYNTAX DEEP-DIVE: COMMON MISUNDERSTANDINGS & RULES

## 2.1 Nested List Comprehension Order
* **The Syntax Rule:** The order of `for` clauses in a list comprehension **matches the exact nesting order of standard `for` loops**!

```python
# Standard Nested Loops:
# for row in matrix:        <-- 1st
#     for val in row:       <-- 2nd
#         if val % 2 == 0:  <-- 3rd
#             result.append(val)

# List Comprehension (Exact Same Order!):
matrix = [[1, 2, 3], [4, 5, 6]]
flattened = [val for row in matrix for val in row]
#            ^^^ ^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^
#          output    1st loop        2nd loop
print(flattened)  # [1, 2, 3, 4, 5, 6]

filtered = [val ** 2 for row in matrix for val in row if val % 2 == 0]
print(filtered)   # [4, 16, 36]
```

---

## 2.2 Slicing Mechanics: `sequence[start:stop:step]`
* `start`: Inclusive starting index. Defaults to `0` (or end if step is negative).
* `stop`: **Exclusive** ending index.
* `step`: Incremental step. Defaults to `1`. Negative step traverses backwards.

```python
data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

print(data[2:7])    # [2, 3, 4, 5, 6] (from index 2 up to, not including, index 7)
print(data[::2])    # [0, 2, 4, 6, 8] (every 2nd element)
print(data[::-1])   # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0] (reversal)
print(data[8:2:-2]) # [8, 6, 4] (backwards stepping from index 8 down to 3)

# Slice Assignment (List mutation):
nums = [1, 2, 3, 4, 5]
nums[1:4] = [20, 30]  # Replaces elements at index 1, 2, 3 with [20, 30]
print(nums)  # [1, 20, 30, 5]
```

---

## 2.3 Packing and Starred Unpacking (`*` and `**`)
* **Single Star `*` on Sequences:** Collects or expands elements into a list or positional arguments.
* **Double Star `**` on Dictionaries:** Expands key-value pairs into keyword arguments or merges dictionaries.

```python
# 1. Starred Assignment (Sequence Unpacking):
first, *middle, last = [10, 20, 30, 40, 50]
print(first)   # 10
print(middle)  # [20, 30, 40] (always unpacked as a list)
print(last)    # 50

# 2. Merging Dictionaries:
d1 = {"a": 1, "b": 2}
d2 = {"b": 99, "c": 3}

# Python 3.5+: Unpacking with **
merged_unpack = {**d1, **d2}
print(merged_unpack)  # {'a': 1, 'b': 99, 'c': 3} (d2 overwrites d1 on conflict)

# Python 3.9+: Dictionary Union Operator '|'
merged_pipe = d1 | d2
print(merged_pipe)    # {'a': 1, 'b': 99, 'c': 3}
```

---

## 2.4 Function Parameter Rules: `/` and `*`
* Parameters **before `/`** are **Positional-Only**.
* Parameters **after `*`** are **Keyword-Only**.
* Parameters in between can be passed positionally or by keyword.

```python
def configure(pos_only, /, standard, *, kw_only):
    print(pos_only, standard, kw_only)

# Valid:
configure(1, 2, kw_only=3)
configure(1, standard=2, kw_only=3)

# Invalid:
# configure(pos_only=1, standard=2, kw_only=3)  -> TypeError: pos_only cannot be keyword
# configure(1, 2, 3)                            -> TypeError: kw_only must be keyword
```

---

## 2.5 `try ... except ... else ... finally`
* `try`: Code that may raise an exception.
* `except`: Runs **only if** an exception occurs.
* `else`: Runs **only if NO exception occurs** in the `try` block.
* `finally`: **Always runs**, regardless of exceptions or `return` statements!

```python
def check_flow(fail: bool):
    try:
        print("1. In Try")
        if fail:
            raise ValueError("Something went wrong")
    except ValueError:
        print("2. In Except (Caught Error)")
    else:
        print("2. In Else (Success, no errors)")
    finally:
        print("3. In Finally (Always executed)")

print("--- No Error ---")
check_flow(fail=False)
# 1. In Try -> 2. In Else -> 3. In Finally

print("--- With Error ---")
check_flow(fail=True)
# 1. In Try -> 2. In Except -> 3. In Finally
```

---

## 2.6 Regular Expressions: Compilation, Matching & Group Extraction
* **Key Patterns & Functions:**
  * `re.compile(pattern, flags)`: Pre-compiles regex into a bytecode pattern object. Highly recommended for repeated matches in loops/APIs.
  * `re.match()`: Checks for a match **only at the beginning** of the string.
  * `re.search()`: Scans through the entire string for the **first occurrence**.
  * `re.finditer()`: Lazily returns an iterator of `Match` objects (memory-efficient for large text/logs).
  * `(?P<name>pattern)`: Named capture group; extracted via `match.group('name')` or `match.groupdict()`.
  * `.*?` vs `.*`: Non-greedy (minimal) vs greedy (maximal) matching.

```python
import re

log_line = '2026-09-06 19:45:00 [ERROR] user_id=4821 - Connection timeout after 350ms'

# Pre-compile with named capture groups and flags:
pattern = re.compile(
    r'(?P<timestamp>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\s'
    r'\[(?P<level>[A-Z]+)\]\s'
    r'user_id=(?P<user_id>\d+)\s-\s'
    r'(?P<message>.*)',
    re.IGNORECASE
)

match = pattern.search(log_line)
if match:
    data = match.groupdict()
    print("Parsed Log:", data)
    # Output: {'timestamp': '2026-09-06 19:45:00', 'level': 'ERROR', 'user_id': '4821', 'message': 'Connection timeout after 350ms'}
    print("Level:", match.group('level'))    # 'ERROR'
    print("Span:", match.span('user_iexplain in more user friendly wayd'))    # (35, 39)
```

---

## 2.7 String Internals, Concatenation & Formatting
* **CPython String Representation:** Python strings are immutable sequences of Unicode characters. CPython represents them using compact structures (`PyASCIIObject`, `PyCompactUnicodeObject`) using 1 byte (Latin-1), 2 bytes (UCS-2), or 4 bytes (UCS-4) per character depending on the maximum code point.
* **Concatenation Performance:**
  * `s += other` inside a loop has an $O(N^2)$ time complexity because strings are immutable; each iteration allocates a new string buffer and copies previous characters.
  * `''.join(list_of_strings)` runs in $O(N)$ time because it pre-calculates the exact total byte length required, allocates memory once, and copies all strings in a single pass.
* **f-Strings (`f"{...}"`):** Evaluated at runtime, faster than `str.format()` or `%` formatting because they are parsed directly into dedicated bytecode (`BUILD_STRING` and `FORMAT_VALUE`).

```python
# ❌ ANTI-PATTERN: O(N^2) memory reallocation
result = ""
for word in ["Senior", "AI", "Engineer"]:
    result += word + " "

# ✅ PRODUCTION IDIOM: O(N) pre-sized single-pass allocation
result_clean = " ".join(["Senior", "AI", "Engineer"])

# Formatting Specifiers in f-strings:
val = 123.4567
pct = 0.8845
num = 42

print(f"Padded Float : {val:10.2f}")   # '    123.46' (10-width, 2 decimals)
print(f"Percentage   : {pct:.1%}")      # '88.5%'
print(f"Binary 8-bit : {num:08b}")      # '00101010'
print(f"Hex Upper    : {num:#06X}")     # '0X002A'
```

---

# 3. MODULE 1: THE PYTHON DATA MODEL, MUTABILITY & MEMORY INTERNALS

## 3.1 CPython Memory Architecture: `PyObject`, `ob_refcnt`, and `ob_type`
In CPython, **everything is an object on the heap**. Every object header contains at least:
1. `ob_refcnt` (`Py_ssize_t`): 64-bit integer tracking active references.
2. `ob_type` (`struct _typeobject*`): Pointer to the object's type object (which defines its methods, dunders, and size).

Variable-length objects (like `list`, `str`, `dict`, `tuple`) are represented as `PyVarObject`, which includes a third field:
3. `ob_size` (`Py_ssize_t`): Number of items currently stored.

```python
import sys

# An integer 0 takes 28 bytes on 64-bit CPython, NOT 4 or 8 bytes:
# - 8 bytes ob_refcnt
# - 8 bytes ob_type pointer
# - 8 bytes ob_size (digits length)
# - 4 bytes digit array alignment
print("Size of 0:", sys.getsizeof(0))       # 28 bytes
print("Size of 1:", sys.getsizeof(1))       # 28 bytes
print("Size of empty list:", sys.getsizeof([]))  # 56 bytes
```

---

## 3.2 List Memory Internals: Dynamic Array & Geometric Growth
* **Representation:** A Python `list` is not a linked list; it is a **dynamic array of pointers** (`PyObject**`).
* **Over-allocation Formula:** When elements are appended and capacity is exceeded, CPython resizes the array using a geometric over-allocation strategy:
  $$\text{new\_allocated} = \text{new\_size} + (\text{new\_size} \gg 3) + (\text{new\_size} < 9 \,?\, 3 : 6)$$
  Capacity progression: $0 \to 4 \to 8 \to 16 \to 24 \to 32 \to 40 \to 52 \dots$
* **Complexity:**
  * `append()`, `pop()` at end: **$O(1)$ amortized**
  * `insert(0, item)`, `pop(0)`: **$O(N)$** because all pointers must be shifted in memory.
  * Access `lst[i]`: **$O(1)$** pointer offset calculation.

```python
import sys

lst = []
prev_size = sys.getsizeof(lst)
print(f"Initial Empty List: {prev_size} bytes")

for i in range(25):
    lst.append(i)
    current_size = sys.getsizeof(lst)
    if current_size != prev_size:
        print(f"Length {len(lst):2d}: Reallocated from {prev_size} to {current_size} bytes")
        prev_size = current_size
```

---

## 3.3 Dictionary & Set Internals: Compact Hash Tables & SipHash
* **Python 3.6+ Compact Dict Architecture:**
  * Legacy Python dicts used a sparse array of 24-byte entry structs (`hash`, `key`, `value`), leading to massive unused memory holes.
  * Modern CPython splits the dictionary into:
    1. A sparse **`indices` array** of small integers (1 byte each for small dicts): `[-1, 0, -1, 1, -1]`
    2. A dense **`entries` array** storing `[hash, key, value]` in insertion order.
  * This architecture reduces memory footprint by 20–25% and makes dictionaries **natively insertion-ordered**.
* **Collision Resolution:** Open addressing with pseudo-random perturbation probing:
  $$i = ((5 \cdot i) + 1 + \text{perturb}) \pmod{2^k}$$
* **SipHash Defense:** Keys are hashed using **SipHash-1-3** with a random seed initialized per Python process (`sys.hash_info`). This prevents algorithmic Hash-DoS attacks where attackers craft colliding keys to degrade $O(1)$ lookups into $O(N)$ denial of service.

```python
# Time Complexities:
# Operation      | Average Case | Pathological Worst Case (Collisions)
# Lookup (d[k])  | O(1)         | O(N)
# Insert (d[k]=v)| O(1)         | O(N)
# Delete (del d) | O(1)         | O(N)

# Hashability demonstration:
class CacheKey:
    def __init__(self, key_id: int):
        self.key_id = key_id

    def __hash__(self):
        return hash(self.key_id)

    def __eq__(self, other):
        if not isinstance(other, CacheKey):
            return False
        return self.key_id == other.key_id

k1 = CacheKey(101)
k2 = CacheKey(101)
store = {k1: "cached_data"}
print(store[k2])  # "cached_data" (k1 and k2 match both __hash__ and __eq__)
```

---

## 3.4 Tuple Internals: Immutability vs Hashability & Free-List Optimization
* **Fixed Memory & Free Lists:** Tuples are immutable arrays of object pointers. Because their size never changes, CPython maintains a free list of up to 2000 unused tuple objects for sizes 1 to 20, bypassing system memory allocator (`malloc`) calls when short-lived tuples are created and destroyed.
* **The Hashability Rule:** A tuple is immutable, but it is **only hashable if every element inside it is also hashable**!

```python
# Hashable Tuple (all items immutable & hashable):
t1 = (1, 2, "hello", (3, 4))
print("t1 hash:", hash(t1))  # Valid

# Unhashable Tuple (contains mutable child):
t2 = (1, 2, [3, 4])
try:
    hash(t2)
except TypeError as e:
    print("Cannot hash t2:", e)  # TypeError: unhashable type: 'list'
```

---

# 4. MODULE 2: SCOPING, FUNCTIONAL MECHANICS & METAPROGRAMMING

## 4.1 Scope Resolution: The LEGB Rule, `global` vs `nonlocal`
* **LEGB Search Order:** Python looks for variables in four hierarchical namespaces:
  1. **L**ocal: Inside current function/lambda.
  2. **E**nclosing: In any enclosing def/closure functions (outer to inner).
  3. **G**lobal: Module-level variables.
  4. **B**uilt-in: Python built-ins (`len`, `range`, `ValueError`).
* **`global`:** Tells Python that an identifier belongs to the top-level module namespace.
* **`nonlocal`:** Binds an identifier to the nearest enclosing (outer) function scope, skipping local and ignoring global. Essential for stateful closures without class overhead.

```python
global_var = "G"

def outer():
    enclosing_var = "E"
    counter = 0

    def inner():
        nonlocal counter, enclosing_var  # Rebind in outer() scope
        global global_var                # Rebind in module scope

        counter += 1
        enclosing_var = "E_MUTATED"
        global_var = "G_MUTATED"
        return counter

    return inner

fn = outer()
print("Count 1:", fn())           # 1
print("Count 2:", fn())           # 2
print("Global Var:", global_var)  # 'G_MUTATED'
```

---

## 4.2 Closures & First-Class Functions: Lexical Scopes & Cell Objects
* **What is a Closure?** A function that retains access to variables from its lexical enclosing scope even after that enclosing function has finished executing and returned.
* **CPython Internals:** The captured variables are stored in the function's `__closure__` attribute as a tuple of **`cell` objects**. Each cell holds a reference (`cell_contents`) to the heap variable.

```python
def make_multiplier(factor: int):
    # 'factor' is captured in the closure:
    def multiply(val: int) -> int:
        return val * factor
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)

print(double(10))  # 20
print(triple(10))  # 30

# Inspecting closure cells:
print("Closure cells:", double.__closure__)
print("Captured factor:", double.__closure__[0].cell_contents)  # 2
```

---

## 4.3 Parameterized Decorators from Scratch: `@retry(max_retries=3, delay=1.0)`
* A decorator with arguments requires **three layers of functions**:
  1. Outer function: Receives configuration arguments (`max_retries`, `delay`, `backoff`).
  2. Middle function: Receives the target function to decorate (`func`).
  3. Inner wrapper: Accepts `*args, **kwargs`, executes retry logic, and returns the result.

```python
import time
import functools
from typing import Callable, Any, Tuple, Type

def retry(
    max_retries: int = 3,
    delay: float = 0.1,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Production retry decorator with exponential backoff and jitter."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        raise e
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator

# Usage:
call_count = 0

@retry(max_retries=3, delay=0.01, backoff=1.5, exceptions=(ValueError,))
def unstable_network_call():
    global call_count
    call_count += 1
    if call_count < 3:
        raise ValueError("Transient 503 Service Unavailable")
    return "SUCCESS_DATA"

print("Result:", unstable_network_call())  # "SUCCESS_DATA" (succeeds on attempt 3)
```

---

## 4.4 Class Decorators & `functools.lru_cache`
* **Class Decorators:** Decorators can wrap or modify entire classes, adding methods, registering them in a plugin registry, or enforcing immutability.
* **`functools.lru_cache`:** Caches function returns in an in-memory dictionary.
  * Parameters: `maxsize=128` (powers of 2 are optimal), `typed=False` (treats `3` and `3.0` as separate keys if `True`).
  * Inspection: `func.cache_info() -> CacheInfo(hits, misses, maxsize, currsize)`.
  * Invalidation: `func.cache_clear()`.

```python
import functools

@functools.lru_cache(maxsize=64, typed=True)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print("Fib(30):", fibonacci(30))
print("Cache Stats:", fibonacci.cache_info())
# CacheInfo(hits=28, misses=31, maxsize=64, currsize=31)
fibonacci.cache_clear()
```

---

## 4.5 Iterators, Generators & `yield from`: Subgenerator Delegation
* **The Iterator Protocol:**
  * Must implement `__iter__()` returning the iterator instance.
  * Must implement `__next__()` returning the next item, or raising `StopIteration`.
* **`yield from <iterable>`:**
  * Establishes a direct bidirectional channel between the caller and the subgenerator.
  * Automatically passes yielded values out to caller, and passes `.send(value)` and `.throw(exc)` back into the active subgenerator.
  * Captures the subgenerator's `return <value>` as the result of the `yield from` expression!

```python
def sub_generator():
    yield "Sub-1"
    yield "Sub-2"
    return "Sub-Finished"

def master_generator():
    yield "Start"
    # yield from delegates iteration and captures return value:
    result = yield from sub_generator()
    yield f"Result: {result}"
    yield "End"

print(list(master_generator()))
# ['Start', 'Sub-1', 'Sub-2', 'Result: Sub-Finished', 'End']
```

---

# 5. MODULE 3: OBJECT-ORIENTED ARCHITECTURE, DUNDERS & INTERNALS

## 5.1 The Dunder Hierarchy & Custom Collection Class
To create a production-grade custom collection that feels native to Python, implement the core dunders:
* `__len__`: for `len(obj)`
* `__getitem__`: for indexing `obj[i]` and slicing
* `__iter__`: for iteration in `for x in obj`
* `__contains__`: for `x in obj` ($O(1)$ set lookup)
* `__repr__` vs `__str__`: `__repr__` is unambiguous for developers; `__str__` is user-friendly.
* `__call__`: allows an instance to be called like a function (e.g., PyTorch `nn.Module(x)`).

```python
from typing import Any, Iterator

class RecordBatch:
    """A high-performance immutable record container."""
    def __init__(self, records: list[dict[str, Any]]):
        self._records = list(records)
        self._id_index = {r["id"]: r for r in self._records if "id" in r}

    def __len__(self) -> int:
        return len(self._records)

    def __getitem__(self, index_or_id: int | str) -> dict[str, Any]:
        if isinstance(index_or_id, int):
            return self._records[index_or_id]
        return self._id_index[index_or_id]

    def __contains__(self, record_id: str) -> bool:
        return record_id in self._id_index

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter(self._records)

    def __repr__(self) -> str:
        return f"RecordBatch(count={len(self._records)}, ids={list(self._id_index.keys())})"

    def __call__(self, filter_key: str, filter_val: Any) -> list[dict[str, Any]]:
        return [r for r in self._records if r.get(filter_key) == filter_val]

# Usage:
batch = RecordBatch([{"id": "doc_1", "score": 0.95}, {"id": "doc_2", "score": 0.81}])
print(len(batch))               # 2 (__len__)
print(batch["doc_1"])           # {'id': 'doc_1', 'score': 0.95} (__getitem__)
print("doc_2" in batch)         # True (__contains__)
print(batch("score", 0.95))     # [{'id': 'doc_1', 'score': 0.95}] (__call__)
```

---

## 5.2 Abstract Base Classes (ABCs): `abc.ABC` & Contract Enforcement
* **Purpose:** Prevent incomplete interface implementations from ever being instantiated at runtime.
* If a class inherits from `abc.ABC` and contains `@abstractmethod` decorators, attempting to instantiate it without overriding **all** abstract methods raises `TypeError: Can't instantiate abstract class ... with abstract method`.

```python
from abc import ABC, abstractmethod
from typing import List

class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        """Fetch documents matching query."""
        pass

class FAISSRetriever(BaseRetriever):
    def __init__(self, index_name: str):
        self.index_name = index_name

    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        return [f"doc_from_{self.index_name}_{i}" for i in range(top_k)]

# BaseRetriever()  # ❌ TypeError: Can't instantiate abstract class
retriever = FAISSRetriever("vector_vault")
print(retriever.retrieve("embedding test", top_k=2))
```

---

## 5.3 Context Managers from Scratch: Class-Based vs `@contextlib.contextmanager`
* **Class-Based Context Manager (`__enter__`, `__exit__`):**
  * `__enter__()`: Sets up resource, returns bound variable (`as res`).
  * `__exit__(exc_type, exc_val, exc_tb)`: Tears down resource. If an exception occurred inside the `with` block, returning `True` **suppresses** the exception from propagating; returning `False` or `None` lets it raise.
* **Generator Pattern (`@contextlib.contextmanager`):**
  * Code before `yield` is `__enter__`.
  * `yield value` passes the bound object to the `as` clause.
  * Code inside `finally` is `__exit__`.

```python
import contextlib
import time

# 1. Class-based with exception suppression:
class DatabaseTransaction:
    def __enter__(self):
        print("BEGIN TRANSACTION")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f"ROLLBACK TRANSACTION due to: {exc_val}")
            return True  # Suppresses exception
        print("COMMIT TRANSACTION")
        return False

with DatabaseTransaction():
    print("Writing records...")
    raise RuntimeError("Disk full!")  # Suppressed by __exit__ returning True!
print("Execution survived rollback.")

# 2. Generator-based with @contextmanager:
@contextlib.contextmanager
def execution_timer(label: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"[{label}] Elapsed time: {elapsed*1000:.3f}ms")

with execution_timer("Vector Normalization"):
    _ = [x ** 0.5 for x in range(100_000)]
```

---

## 5.4 Object Allocation & Metaprogramming: `__new__` vs `__init__` & Thread-Safe Singleton
* `__new__(cls)` is the **allocator**: a static method that allocates memory and returns a brand-new instance of `cls`.
* `__init__(self)` is the **initializer**: takes the allocated instance and configures attributes.
* **Thread-Safe Singleton with Double-Checked Locking:**

```python
import threading

class ThreadSafeSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_val: str = "default"):
        self.config_val = config_val

s1 = ThreadSafeSingleton("production")
s2 = ThreadSafeSingleton("staging")
print("Are instances identical?", s1 is s2)  # True
print("Shared config:", s1.config_val)         # 'staging' (re-initialized)
```

---

# 6. MODULE 4: MODERN TYPING, CONCURRENCY & ASYNCIO

## 6.1 Modern Python Typing: `TypeVar`, `Generic`, `Callable`, and `Protocol`
* **`TypeVar` & `Generic[T]`:** Enables parameterized classes/functions without sacrificing static type checking.
* **`typing.Protocol` (Static Duck Typing):** Structural subtyping. A class satisfies a `Protocol` if it implements the required methods and attributes, **without explicitly inheriting from it**!
* **Python 3.10+ Native Types:**
  * Use `X | Y` instead of `Union[X, Y]`
  * Use `X | None` instead of `Optional[X]`
  * Built-in collections are generic: `list[str]`, `dict[str, int]` instead of importing `List`, `Dict`.

```python
from typing import TypeVar, Generic, Protocol, runtime_checkable

T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

# Structural Subtyping via Protocol:
@runtime_checkable
class VectorIndex(Protocol):
    def search(self, vector: list[float], top_k: int) -> list[str]: ...

class MockFaiss:
    """Matches VectorIndex protocol WITHOUT explicitly subclassing it!"""
    def search(self, vector: list[float], top_k: int) -> list[str]:
        return ["doc_1", "doc_2"][:top_k]

idx = MockFaiss()
print("Satisfies VectorIndex?", isinstance(idx, VectorIndex))  # True
```

---

## 6.2 Pydantic V2 Architecture: `BaseModel`, `@field_validator`, and `@model_validator`
* **Pydantic V2 Core:** Powered by the Rust `pydantic-core` engine, offering 5–20x faster validation and serialization than V1.
* **`@field_validator`:**
  * `mode='before'`: Runs on raw input data before Pydantic coercion.
  * `mode='after'` (default): Runs after Pydantic validates the type.
* **`@model_validator(mode='after')`:** Replaces root validators; used for cross-field consistency checks.
* **Serialization:** Use `.model_dump()` (returns dict) and `.model_dump_json()` (returns JSON string), replacing legacy `.dict()` and `.json()`.

```python
from pydantic import BaseModel, Field, field_validator, model_validator

class LLMQueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    top_k: int = Field(default=5, ge=1, le=50)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    system_prompt: str | None = None

    @field_validator("query", mode="after")
    @classmethod
    def strip_and_clean_query(cls, v: str) -> str:
        return v.strip()

    @model_validator(mode="after")
    def validate_deterministic_temp(self) -> "LLMQueryRequest":
        # If temperature is 0, system_prompt must not be empty:
        if self.temperature == 0.0 and not self.system_prompt:
            self.system_prompt = "You are a precise, deterministic AI assistant."
        return self

req = LLMQueryRequest(query="  Explain Jensen-Shannon Divergence  ", temperature=0.0)
print(req.query)          # "Explain Jensen-Shannon Divergence" (stripped)
print(req.system_prompt)  # Set by model_validator
print(req.model_dump())   # Clean dictionary export
```

---

## 6.3 Concurrency Architecture: Threading vs Multiprocessing vs Asyncio Decision Matrix

| Dimension | `threading` | `multiprocessing` | `asyncio` |
| :--- | :--- | :--- | :--- |
| **Execution Model** | Preemptive OS threads | Preemptive OS processes | Cooperative single thread (Event Loop) |
| **GIL Constraint** | **Bound by GIL** (No multi-core CPU parallelism) | **Bypasses GIL** (Separate interpreter per core) | **Bound by GIL** (Runs on 1 thread) |
| **Memory Footprint** | Low (~8MB stack per thread) | High (Full duplicate memory space) | **Extremely Low** (~few KBs per coroutine) |
| **Context Switching**| OS Kernel interrupt | OS Process scheduler | **Voluntary via `await` points** |
| **IPC / Sharing** | Shared memory (Need `Lock`, `RLock`) | Inter-Process Comm (`Queue`, `Pipe`, `shared_memory`) | Shared memory (No thread race hazards) |
| **Optimal Use Case** | Legacy blocking I/O, background daemon watchers | **CPU-bound ML/Math**, data processing, tokenization | **High-concurrency network I/O**, WebSockets, LLM APIs |

---

## 6.4 Asyncio Production Patterns: Tasks, `gather`, Timeouts, Cancellation & Semaphores
* **Task Scheduling:** `asyncio.create_task(coro)` schedules execution concurrently on the event loop.
* **Resilient Gathering:** `asyncio.gather(*tasks, return_exceptions=True)` prevents a single failing task from blowing up all other concurrent tasks.
* **Concurrency Throttling:** `asyncio.Semaphore(max_concurrent)` limits simultaneous connections (e.g. rate-limiting LLM API calls).
* **Timeouts:** Python 3.11+ `async with asyncio.timeout(secs):` context manager cleanly cancels slow tasks.

```python
import asyncio
import random

async def fetch_llm_response(doc_id: int, sem: asyncio.Semaphore) -> str:
    async with sem:  # Throttles max concurrent API calls
        # Simulating external network latency:
        latency = random.uniform(0.05, 0.15)
        await asyncio.sleep(latency)
        if doc_id == 13:
            raise ConnectionResetError("Remote API 429 Rate Limit")
        return f"Response for doc {doc_id}"

async def main():
    sem = asyncio.Semaphore(5)  # Max 5 concurrent tasks
    tasks = [fetch_llm_response(i, sem) for i in range(20)]

    # return_exceptions=True captures exceptions alongside successful values:
    results = await asyncio.gather(*tasks, return_exceptions=True)

    successes = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, Exception)]

    print(f"Total: {len(results)} | Successes: {len(successes)} | Failures: {len(failures)}")
    print("Captured Failure:", failures[0])

# asyncio.run(main())
```

---

# 7. MODULE 5: HIGH-FREQUENCY LIVE-CODING IMPLEMENTATIONS

## 7.1 LRU Cache ($O(1)$ Time Complexity)
```python
class DListNode:
    def __init__(self, key=0, val=0):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None

class LRUCache:
    """Hash Map + Doubly Linked List for O(1) Get and Put."""
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> DListNode
        self.head = DListNode()  # Dummy head
        self.tail = DListNode()  # Dummy tail
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: DListNode):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node: DListNode):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_to_front(node)  # Mark recently used
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
            node.val = value
            self._add_to_front(node)
        else:
            if len(self.cache) >= self.capacity:
                # Evict least recently used (node before tail)
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]
            new_node = DListNode(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
```

---

## 7.2 Token Bucket Rate Limiter (Thread-Safe)
```python
import time
import threading

class TokenBucketRateLimiter:
    """Thread-safe rate limiter with burst capability."""
    def __init__(self, rate_per_sec: float, capacity: float):
        self.rate = rate_per_sec
        self.capacity = capacity
        self.tokens = capacity
        self.last_refreshed = time.monotonic()
        self.lock = threading.Lock()

    def allow(self, tokens_requested: float = 1.0) -> bool:
        with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_refreshed
            self.last_refreshed = now

            # Refill tokens:
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)

            if self.tokens >= tokens_requested:
                self.tokens -= tokens_requested
                return True
            return False
```

---

## 7.3 High-Throughput Streaming & Chunking Generator
Used extensively in enterprise RAG pipelines, LLM token streaming, and large dataset ingestion to prevent out-of-memory errors by processing continuous streams into fixed-size batches.

```python
from typing import Iterable, Iterator, TypeVar, List

T = TypeVar("T")

def chunked_stream(stream: Iterable[T], chunk_size: int) -> Iterator[List[T]]:
    """
    Lazily consumes an arbitrary stream/iterator and yields batches of size chunk_size.
    Memory footprint: O(chunk_size), strictly independent of total stream volume.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    chunk = []
    for item in stream:
        chunk.append(item)
        if len(chunk) == chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk  # Yield remaining tail elements

# Usage:
data_stream = (f"token_{i}" for i in range(11))
for batch in chunked_stream(data_stream, chunk_size=4):
    print("Stream Batch:", batch)
# Stream Batch: ['token_0', 'token_1', 'token_2', 'token_3']
# Stream Batch: ['token_4', 'token_5', 'token_6', 'token_7']
# Stream Batch: ['token_8', 'token_9', 'token_10']
```

---

# 8. MODULE 6: EDGE-CASES, SYNTAX GOTCHAS & "WHAT DOES THIS OUTPUT?"

### Gotcha 1: Modifying a List While Iterating Over It
```python
# ❌ THE TRAP:
nums = [1, 2, 3, 4, 5]
for n in nums:
    if n % 2 == 1:
        nums.remove(n)
print(nums)  # Output: [2,4]
# Why? Removing index 0 shifts '2' to index 0, but the loop pointer advances to index 1, skipping '2'.
# Later, removing '3' shifts '4' to index 2, skipping '4'.

# ✅ THE FIX (Iterate over a shallow copy or use a comprehension):
nums = [1, 2, 3, 4, 5]
nums = [n for n in nums if n % 2 == 0]
print("Clean:", nums)  # [2, 4]
```

---

### Gotcha 2: Chained Comparisons Evaluate Middle Operands Exactly Once
```python
def check(val):
    print(f"Called check({val})")
    return val

# 1 < check(3) < 5 evaluates:
# (1 < 3) and (3 < 5), but check(3) is called ONLY ONCE!
result = 1 < check(3) < 5
# Prints: "Called check(3)" once.
print("Result:", result)  # True
```

---

### Gotcha 3: Variable Scope Leakage in Loops vs Comprehensions
```python
# 1. for-loops LEAK their loop variable into the enclosing function scope:
for loop_var in range(5):
    pass
print("Leaked loop_var:", loop_var)  # 4!

# 2. In Python 3+, comprehensions have their OWN local scope and DO NOT leak:
[comp_var for comp_var in range(5)]
try:
    print(comp_var)
except NameError as e:
    print("comp_var is isolated:", e)  # NameError: name 'comp_var' is not defined
```

---

### Gotcha 4: Float NaN Equality and Hash Map Behavior
```python
# float('nan') is never equal to anything, including itself:
nan1 = float("nan")
nan2 = float("nan")
print(nan1 == nan2)  # False!

# But in a dictionary:
d = {nan1: "Value 1"}
print(nan1 in d)  # True (Python checks `is` (identity) before `==`!)
print(nan2 in d)  # False (Different object identity, and == returns False!)
```

---

### Gotcha 5: `finally` Block Overriding Returns and Silencing Exceptions
```python
def dangerous_return():
    try:
        raise RuntimeError("Fatal system error")
        return "TRY_RESULT"
    finally:
        return "FINALLY_OVERRIDE"

# What does this output?
# It prints "FINALLY_OVERRIDE"! The RuntimeError is SILENTLY DISCARDED!
# Rule: NEVER execute a 'return' or 'break' inside a finally block.
print("Result:", dangerous_return())  # 'FINALLY_OVERRIDE'
```

