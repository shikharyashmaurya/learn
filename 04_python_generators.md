# Drill 1.4: Step 1 Mental Models & Pointer Mechanics

## Topic: Iterators, Generators, `yield from` & Memory Profiling

---

### 1. The Iterator Protocol vs The Iterable Protocol
In Python, iteration is governed by two strict dunder contracts:

```
[ Iterable Object ]  (e.g., list, dict, str, custom collection)
        |
        |  calls iter(obj)  -->  invokes obj.__iter__()
        v
[ Iterator Object ]  (has mutable iteration state)
        |
        +---> __iter__()    --> returns self
        |
        +---> __next__()    --> returns next item
                                 OR raises StopIteration
```

#### Under the Hood: What a `for` Loop Actually Does
```python
for item in collection:
    process(item)

# CPython executes this exact bytecode sequence:
_iterator = iter(collection)    # collection.__iter__()
while True:
    try:
        item = next(_iterator)  # _iterator.__next__()
    except StopIteration:
        break
    process(item)
```

* **Iterable:** Must define `__iter__()` returning an Iterator.
* **Iterator:** Must define `__iter__()` (returning `self`) AND `__next__()` (returning values or raising `StopIteration`).
* **Key Invariant:** An iterator is stateful and one-way. Once consumed to `StopIteration`, it cannot be reset; a new iterator must be created from the iterable.

---

### 2. Generators & Frame Suspension: $O(1)$ Memory Mechanics
A **generator function** is any function containing the `yield` keyword.
When invoked, it does **not** execute the function body; instead, CPython creates and returns a **`PyGenObject`** (generator iterator).

```
Normal Function Call:
[ Create Stack Frame ] -> [ Execute to return ] -> [ POP & DESTROY FRAME ]

Generator Execution:
gen = stream_fn()      --> PyGenObject created on heap (frame NOT executing yet)

next(gen):
[ RESUME FRAME ] ----> executes until `yield value` ----> [ SUSPEND FRAME ]
                                                               |
                                            Stores instruction pointer (f_lasti)
                                            and local variables (f_locals) on HEAP!

next(gen):
[ RESUME FRAME ] ----> resumes from f_lasti ----> yields or terminates (StopIteration)
```

#### Memory Impact in AI/ML Pipelines
* **Eager Materialization:** `[process(x) for x in dataset]` loads all $N$ items into memory at once ($O(N)$ RAM). On 10M vectors or tokens, this crashes the container (`OOM Killed`).
* **Lazy Streaming:** `(process(x) for x in dataset)` yields one item at a time on-demand ($O(1)$ RAM). Memory usage remains constant regardless of dataset size.

---

### 3. Subgenerator Delegation: `yield from`
`yield from <subgenerator>` replaces manual looping and establishes a transparent **bidirectional communication tunnel** between the outer caller and the inner subgenerator.

```
Caller  <==================== bidirectional tunnel ====================>  Subgenerator
(e.g. next(), .send())                 (via yield from)                    (inner generator)
```

#### Why `yield from` is More than `for x in subgen: yield x`:
1. **Direct Value Tunneling:** Items yielded by the subgenerator bypass the delegating generator directly to the caller.
2. **Exception & Signal Passing:** `.send(val)`, `.throw(exc)`, and `.close()` invoked on the master generator are routed directly into the subgenerator.
3. **Capturing Return Values:** When a Python generator executes `return "result"`, it raises `StopIteration("result")`. `yield from` catches that exception and extracts the returned value:
   ```python
   def sub():
       yield 1
       yield 2
       return "COMPLETED"

   def delegator():
       # The return value of the subgenerator is captured by assignment:
       res = yield from sub()
       yield f"Subgenerator returned: {res}"
   ```

---

### 4. Generator Coroutines & Two-Way Communication via `.send()`
`yield` is not only an output statement; it is also an **expression** that can evaluate to a value received from the caller!

```
Caller calls: gen.send("INJECTED_VALUE")
                         |
                         v
Inside generator: received = yield current_count
                                ^
                                |
             (Suspends and outputs current_count;
              resumes and assigns "INJECTED_VALUE" to `received`)
```

#### The Priming Requirement
* A newly created generator is in state `GEN_CREATED` (execution has not started).
* You **cannot** send a non-None value to a newly created generator:
  `TypeError: can't send non-None value to a just-started generator`.
* **Rule:** You must first **prime** the generator by advancing it to its first `yield` statement using `next(gen)` or `gen.send(None)`.

---

### 5. Infinite Streams & Window Slicing (`itertools.islice`)
In LLM streaming telemetry, agent heartbeats, or log watchers, data sources can be infinite:

```python
def infinite_sequence():
    idx = 0
    while True:
        yield idx
        idx += 1
```

* **The Trap:** Passing an infinite generator to `list(infinite_sequence())` hangs forever and exhausts memory.
* **The Solution:** Use `itertools.islice(iterable, stop)` or `itertools.islice(iterable, start, stop, step)` to pull exactly $K$ items lazily without consuming the entire stream.
* `islice` advances the underlying iterator in-place without copying or buffering all prior items in memory.
