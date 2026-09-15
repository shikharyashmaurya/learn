"""
==============================================================================
DRILL 1.1: PYTHON DATA MODEL, MUTABILITY & COMPREHENSIONS
==============================================================================
Target: Master memory references, pass-by-assignment, object identity, and
idiomatic container transformations with zero autocomplete.

Instructions:
1. Implement each function marked with TODO. Do not import external libraries.
2. Run this file directly with Python:
      python drills/01_python_mutability.py
3. All assertions in run_tests() must PASS.
==============================================================================
"""

import copy


# ----------------------------------------------------------------------
# TASK 1: Pass-by-Assignment & Pointer Rebinding
# ----------------------------------------------------------------------
def mutate_vs_rebind(original_list: list, append_val: int) -> None:
    """
    Requirements:
    1. Append `append_val` to `original_list` in-place (the caller's reference
       MUST reflect this change).
    2. Rebind the local identifier `original_list` to a new list [999, 1000].
    3. The function returns None.
    """
    # TODO: Implement step 1 and step 2
    original_list.append(append_val)
    original_list=[999,1000]


# ----------------------------------------------------------------------
# TASK 2: Mutable Default Argument Trap
# ----------------------------------------------------------------------
class EventRegistry:
    """
    Fix the classic mutable default argument trap.
    An instance should record events for a specific subsystem.
    If no initial_events list is provided, each instance MUST have its own
    independent list, NOT shared across class instances.
    """
    def __init__(self, subsystem: str, initial_events=None):
        # TODO: Implement the safe default argument idiom
        self.subsystem = subsystem
        if initial_events is None:
            self.events=[]
        else:
            self.events=list(initial_events)
        
    def add_event(self, event_name: str) -> list:
        # TODO: Add event to this instance's events and return the list
        self.events.append(event_name)
        return self.events

# ----------------------------------------------------------------------
# TASK 3: Shallow Copy vs Deep Copy Simulation
# ----------------------------------------------------------------------
def clone_and_mutate_nested(data: list) -> tuple:
    """
    Given a nested list: e.g. [[1, 2], [3, 4]]
    
    1. Create a SHALLOW copy named `shallow`
    2. Create a DEEP copy named `deep`
    3. Modify `data[0][0] = 99`
    4. Return (shallow, deep)
    
    Predict & demonstrate:
    - What is shallow[0][0]?
    - What is deep[0][0]?
    """
    # TODO: Implement shallow & deep copy, apply the mutation to data, and return (shallow, deep)
    shallow=copy.copy(data)
    deep=copy.deepcopy(data)
    data[0][0]=99
    return (shallow,deep)


# ----------------------------------------------------------------------
# TASK 4: Advanced Matrix Flattening & Filtering Comprehension
# ----------------------------------------------------------------------
def flatten_even_positive_numbers(matrix: list[list[int]]) -> list[int]:
    """
    Using a SINGLE list comprehension:
    Flatten a 2D matrix of integers, keeping only positive numbers ( > 0 )
    that are ALSO even ( x % 2 == 0 ).
    Order must preserve row-major traversal.
    
    Example:
    matrix = [
        [-2, 4, 3],
        [6, -8, 10],
        [1, 3, 5]
    ]
    Result -> [4, 6, 10]
    """
    # TODO: Return single list comprehension
    return [j for i in matrix for j in i if j>0 and j%2==0]


# ----------------------------------------------------------------------
# TASK 5: Inverted Dictionary with Collision Handling
# ----------------------------------------------------------------------
def invert_dictionary_grouped(mapping: dict[str, int]) -> dict[int, list[str]]:
    """
    Invert a key-value dictionary where values become keys.
    Because multiple original keys can map to the same value, group all original keys in a sorted list under their new key.
    
    Must be implemented cleanly without external libraries.
    
    Example:
    mapping = {"a": 1, "b": 2, "c": 1, "d": 3, "e": 2}
    Result -> {1: ["a", "c"], 2: ["b", "e"], 3: ["d"]}
    """
    # TODO: Implement dictionary inversion with sorted collision lists
    inverted={}
    for key,value in mapping.items():
        if value not in inverted:
            inverted[value]=[]
        inverted[value].append(key)

    for key in inverted:
        inverted[key].sort()

    return inverted

# ======================================================================
# VERIFICATION SUITE
# ======================================================================
def run_tests():
    print("Running Drill 1.1 tests...\n")

    # --- Test 1: Mutate vs Rebind ---
    outer_list = [10, 20]
    mutate_vs_rebind(outer_list, 30)
    assert outer_list == [10, 20, 30], f"Test 1 Failed: expected [10, 20, 30], got {outer_list}"
    print("✅ Task 1 Passed: Pass-by-assignment & pointer rebinding verified.")

    # --- Test 2: Mutable Default Argument ---
    reg1 = EventRegistry("auth")
    reg1.add_event("login")
    reg2 = EventRegistry("billing")
    reg2.add_event("charge")
    assert reg1.events == ["login"], f"Test 2 Failed: reg1 shared state: {reg1.events}"
    assert reg2.events == ["billing_init", "charge"] or reg2.events == ["charge"], f"Test 2 Failed: reg2: {reg2.events}"
    assert reg1.events is not reg2.events, "Test 2 Failed: reg1 and reg2 share the same list in memory!"
    print("✅ Task 2 Passed: Mutable default argument trap resolved.")

    # --- Test 3: Shallow vs Deep Copy ---
    source = [[1, 2], [3, 4]]
    shallow, deep = clone_and_mutate_nested(source)
    assert source[0][0] == 99, "Source list was not modified as instructed."
    assert shallow[0][0] == 99, f"Shallow copy should reflect inner mutation! Got {shallow[0][0]}"
    assert deep[0][0] == 1, f"Deep copy must remain isolated! Expected 1, got {deep[0][0]}"
    assert shallow is not source, "Shallow copy outer container must have different id from source."
    assert shallow[0] is source[0], "Shallow copy inner element must reference identical object as source[0]."
    assert deep[0] is not source[0], "Deep copy inner element must be a completely separate object."
    print("✅ Task 3 Passed: Shallow vs Deep copy memory mechanics verified.")

    # --- Test 4: Matrix Flattening Comprehension ---
    matrix = [
        [-4, 2, 5, -1],
        [8, 10, -6, 3],
        [0, 12, 7, 14]
    ]
    flattened = flatten_even_positive_numbers(matrix)
    assert flattened == [2, 8, 10, 12, 14], f"Test 4 Failed: got {flattened}"
    print("✅ Task 4 Passed: Matrix flattening & filtering comprehension verified.")

    # --- Test 5: Inverted Dictionary ---
    sample_map = {"model_a": 128, "model_b": 256, "model_c": 128, "model_d": 512, "model_e": 256}
    inverted = invert_dictionary_grouped(sample_map)
    expected = {
        128: ["model_a", "model_c"],
        256: ["model_b", "model_e"],
        512: ["model_d"]
    }
    assert inverted == expected, f"Test 5 Failed: expected {expected}, got {inverted}"
    print("✅ Task 5 Passed: Dictionary inversion with collision handling verified.")

    print("\n🎉 ALL DRILL 1.1 TESTS PASSED! Ready for Step 3: Interview Grilling.")


if __name__ == "__main__":
    run_tests()
