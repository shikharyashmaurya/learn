# Drill 1.1: Step 1 Mental Models & Pointer Mechanics

## Topic: Python Data Model, Mutability & Comprehensions

---

### 1. Pass-by-Assignment: Rebinding vs. In-Place Mutation
Python does **not** pass by value or pass by reference. It uses **call-by-object-reference** (pass-by-assignment). Arguments receive a *copy of the reference (pointer)* to the heap object.

```
STACK (Local Names)                      HEAP (Objects)
-------------------                      --------------
caller: my_list ----------------------> [ id: 0x100 ] -> [10, 20]
                                            ^
func:   original_list ----------------------+
```

* **In-Place Mutation (`original_list.append(30)`):** Operates directly on heap object `0x100`. Both `caller` and `func` point here, so the caller **sees** `[10, 20, 30]`.
* **Rebinding (`original_list = [999, 1000]`):** Changes the local pointer `original_list` to point to a *new* heap object `0x200`. The caller’s `my_list` remains pointed at `0x100`.

---

### 2. Shallow vs. Deep Copy
```
SHALLOW COPY:
source:   [ id: 0xA ]  ---> [ elem_0: id 0xB,  elem_1: id 0xC ]
                              |                  |
                              v                  v
                           [1, 2]             [3, 4]
                              ^                  ^
                              |                  |
shallow:  [ id: 0xD ]  ---> [ elem_0: id 0xB,  elem_1: id 0xC ]
* Outer container is new (0xD != 0xA).
* Inner elements are shared references (id 0xB == id 0xB). Mutating source[0][0] mutates shallow[0][0]!

DEEP COPY:
deep:     [ id: 0xE ]  ---> [ elem_0: id 0xF,  elem_1: id 0x10 ]
                              |                  |
                              v                  v
                           [1, 2]             [3, 4]
* Recursively cloned. Complete memory isolation.
```

---

### 3. The Mutable Default Argument Trap
```python
def log_event(event, log=[]):  # ⚠️ Evaluated ONCE at function definition time!
    log.append(event)
    return log
```
The empty list is bound to `log_event.__defaults__` when the file compiles. Every subsequent call without `log` reuses the identical heap object.
* **The Senior Idiom:** Set default to `None` and instantiate `if log is None: log = []` inside the body.

---

### 4. Nested Comprehension Traversal Order
To flatten a matrix:
```python
[item for row in matrix for item in row if condition]
#      ^^^^^^^^^^^^^^^^  ^^^^^^^^^^^^^^  ^^^^^^^^^^^^
#           Loop 1           Loop 2        Filter
```
It reads in the **exact same order** you would write nested `for` statements.
