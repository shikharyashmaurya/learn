# Drill 1.2: Step 1 Mental Models & Pointer Mechanics

## Topic: Collections Internals, Hashability, Slicing & Unpacking

---

### 1. List Internals: Contiguous Pointer Array & Geometric Resizing
A Python `list` is **not** a linked list. It is a **dynamically resized array of pointers (`PyObject**`)** pointing to heap objects.

```
Python list object (PyVarObject):
+---------------+---------------+---------------+--------------------+
|  ob_refcnt    |   ob_type     |    ob_size    |  allocated slots   |
|   (8 bytes)   |  (list type)  |  (3 elements) |     (6 slots)      |
+---------------+---------------+---------------+--------------------+
                                                        |
                                                        v
  Contiguous Pointer Array in Memory:
  [ Slot 0 ] ----> PyObject (int: 10)
  [ Slot 1 ] ----> PyObject (str: "AI")
  [ Slot 2 ] ----> PyObject (list: [1, 2])
  [ Slot 3 ] ----> NULL (Pre-allocated unused buffer)
  [ Slot 4 ] ----> NULL (Pre-allocated unused buffer)
  [ Slot 5 ] ----> NULL (Pre-allocated unused buffer)
```

* **Access `lst[i]` is $O(1)$**: Simple address arithmetic: `base_ptr + (i * pointer_size)`.
* **`lst.append(x)` is Amortized $O(1)$**: When capacity is reached, CPython over-allocates geometrically:
  $$\text{capacity} \approx \text{size} + (\text{size} \gg 3) + (\text{size} < 9 \,?\, 3 : 6)$$
  Resizing requires allocating a new, larger memory block and copying pointers ($O(N)$ spike), but it happens exponentially less often.
* **`lst.insert(0, x)` or `lst.pop(0)` is $O(N)$**: Requires shifting all $N$ pointers right or left by one slot using `memmove`.

---

### 2. Modern Dict Internals: Compact Hash Table (Python 3.6+)
Legacy Python dicts stored `[hash, key, value]` in a single sparse table with 24 bytes per bucket, creating large memory gaps.
Modern CPython splits storage into two tables:

```
SPARSE INDICES ARRAY (Small ints: 1 byte each):
Hash index:    0      1      2      3      4      5      6      7
Indices:    [ -1,     0,    -1,     1,    -1,    -1,     2,    -1 ]
                      |             |                    |
                      v             v                    v
DENSE ENTRIES ARRAY (Appended sequentially in insertion order):
Index 0: { hash: 0x48A1..., key: "id",    value: 101 }
Index 1: { hash: 0x9B2C..., key: "role",  value: "agent" }
Index 2: { hash: 0x1F3E..., key: "model", value: "gemini" }
```

* **Why Dicts Preserve Insertion Order:** New keys are appended sequentially to the next open slot in the dense `entries` array!
* **Memory Savings:** 20% to 25% less RAM than sparse tables.
* **Collision Probing:** Open addressing with perturbation: $i = ((5 \cdot i) + 1 + \text{perturb}) \pmod{\text{size}}$.
* **Hash-DoS Defense (SipHash):** Python hashes strings with a randomized secret seed per process (`sys.hash_info`), preventing attackers from crafting colliding keys to force worst-case $O(N)$ lookups.

---

### 3. The Hashability Contract (`__hash__` & `__eq__`)
For an object to serve as a **dict key** or inside a **set**, it MUST satisfy two rules:

1. **Invariance:** Its hash value must never change across its lifetime.
2. **The Golden Invariant:** If `a == b`, then `hash(a) == hash(b)` **MUST ALWAYS BE TRUE**.
   *(Note: The reverse is NOT required: two unequal objects can have the same hash — this is a collision).*

```
                     IS IT HASHABLE?
                            |
           +----------------+----------------+
           |                                 |
       MUTABLE?                         IMMUTABLE?
    (list, dict, set)                (int, str, bytes)
           |                                 |
     ❌ NO (__hash__ = None)            ✅ YES (Built-in hash)
                                             |
                                          TUPLE?
                                             |
                              +--------------+--------------+
                              |                             |
                       All items hashable?         Contains mutable item?
                       e.g. (1, "a", (2, 3))        e.g. (1, [2, 3])
                              |                             |
                           ✅ YES                        ❌ NO (TypeError)
```

---

### 4. Slicing & Unpacking Visual Cheat-Sheet

#### Slicing: `sequence[start:stop:step]`
```
Index:    0    1    2    3    4    5
Array:  [ A,   B,   C,   D,   E,   F ]
Neg:     -6   -5   -4   -3   -2   -1

data[1:4]   -> [ B, C, D ]         (1 to 3, excludes 4)
data[::-1]  -> [ F, E, D, C, B, A ](Reverse step)
data[4:1:-1]-> [ E, D, C ]         (Walks backwards from 4 down to 2)
```

#### Starred Unpacking:
```python
first, *middle, last = [10, 20, 30, 40, 50]
# first  = 10
# middle = [20, 30, 40]   <-- ALWAYS a list, regardless of input iterable
# last   = 50

# Dictionary merge:
d1 = {"a": 1, "b": 2}
d2 = {"b": 99, "c": 3}
merged = d1 | d2           # {"a": 1, "b": 99, "c": 3} (right-hand overwrites)
```
