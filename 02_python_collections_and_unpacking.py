"""
==============================================================================
DRILL 1.2: COLLECTIONS INTERNALS, HASHABILITY & UNPACKING
==============================================================================
Target: Master CPython list/dict/set/tuple internals, hashability contracts,
slicing mechanics, and sequence unpacking with zero copilot.

Instructions:
1. Implement each function marked with TODO.
2. Run this file directly with Python:
      python drills/02_python_collections_and_unpacking.py
3. All assertions in run_tests() must PASS.
==============================================================================
"""

from importlib import _bootstrap_external
import sys
from typing import Any, List, Tuple, Dict, Set


# ----------------------------------------------------------------------
# TASK 1: The Hashability Contract (__hash__ and __eq__)
# ----------------------------------------------------------------------
class GraphNodeKey:
    """
    In CodeTree and LangGraph, graph nodes need unique, hashable identifiers
    so they can be stored in sets and used as dict keys in adjacency maps.

    Requirements:
    1. An instance is initialized with `node_id: str` and `version: int`.
    2. Instances are considered equal (`__eq__`) if and only if BOTH `node_id`
       and `version` match.
    3. Implement `__hash__` such that the hashability invariant is preserved:
       If `a == b`, then `hash(a) == hash(b)` MUST be true.
    4. Two distinct instances with the same (node_id, version) MUST resolve
       to the SAME dictionary key and MUST NOT create duplicates in a set.
    """
    def __init__(self, node_id: str, version: int):
        self.node_id = node_id
        self.version = version

    def __eq__(self, other: Any) -> bool:
        # TODO: Implement equality check
        if self.node_id==other.node_id and self.version==other.version:
            return True
        else:
            return False

    def __hash__(self) -> int:
        # TODO: Implement hash function maintaining the hash invariant
        # return int(hash(self.node_id))
        return hash((self.node_id, self.version))



# ----------------------------------------------------------------------
# TASK 2: Advanced Slicing & In-Place Slice Mutation
# ----------------------------------------------------------------------
def reverse_alternate_elements(items: list) -> list:
    """
    Requirements:
    Return a NEW list containing elements from `items` traversed in REVERSE,
    taking every 2nd element starting from the last element.
    Example: [0, 1, 2, 3, 4, 5] -> [5, 3, 1]
    Must be solved using a SINGLE slice expression!
    """
    # TODO: Implement using a single slice
    return items[::-2]


def replace_middle_slice(target_list: list, start: int, end: int, replacement: list) -> None:
    """
    Requirements:
    1. Replace elements of `target_list` from index `start` up to `end` (exclusive)
       with the elements of `replacement` IN-PLACE.
    2. The caller's list reference MUST be modified directly (do NOT rebind `target_list = ...`).
    3. The function returns None.
    Example: target = [1, 2, 3, 4, 5], start=1, end=4, replacement=[20, 30]
             target becomes [1, 20, 30, 5]
    """
    # TODO: Implement using slice assignment
    target_list[start:end]=replacement


# ----------------------------------------------------------------------
# TASK 3: Starred Unpacking & Config Merge
# ----------------------------------------------------------------------
def parse_agent_payload(payload: list) -> Tuple[str, list, str]:
    """
    An agent payload arrives as a variable-length list containing at least 2 items:
    - First item: `sender_id` (str)
    - Last item: `checksum` (str)
    - All items in between: `messages` (list of intermediate items)

    Requirements:
    1. Unpack `payload` using starred expression syntax in a single assignment.
    2. Return a tuple: `(sender_id, messages, checksum)`.
    3. If payload has only 2 items, `messages` MUST be an empty list `[]`.
    """
    # TODO: Implement with starred unpacking
    (x,*y,z)=payload
    return x,list(y),z


def merge_configurations(base_config: dict, env_config: dict, cli_overrides: dict) -> dict:
    """
    Merge three configuration dictionaries with ascending priority:
    `cli_overrides` overrides `env_config`, which overrides `base_config`.

    Requirements:
    1. Return a single merged dictionary.
    2. The original input dictionaries MUST remain unmutated.
    3. Use modern Python dictionary merging idioms (unpacking `**` or `|` operator).
    """
    # Fix: Use ** (double-star) for dict unpacking, or Python 3.9+ '|' union pipe:
    return base_config | env_config | cli_overrides


# ----------------------------------------------------------------------
# TASK 4: Deduplicate Unhashable Items Preserving Order
# ----------------------------------------------------------------------
def deduplicate_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    In RAG chunking and agent memories, records often arrive as dictionaries
    (which are unhashable mutable objects: `TypeError: unhashable type: 'dict'`).

    Requirements:
    1. Deduplicate a list of dictionaries based on identical content.
    2. Preserve the ORIGINAL insertion order of first appearance.
    3. Do NOT use external libraries (no pandas).
    4. Hint: Think about how to convert each dict into an immutable, hashable
       representation (e.g. sorted tuple of key-value pairs) for O(1) set lookups!
    """
    # TODO: Deduplicate while preserving order and handling unhashable dicts
    # a=dict()
    # b=[]
    # for i in records:
    #     j,k=i.items()
    #     if (j,k) not in a:
    #         a[(j,k)]=1
    #         b.append(i)
    # return b

    seen = set()
    result = []
    for rec in records:
        marker = tuple(sorted(rec.items()))
        if marker not in seen:
            seen.add(marker)
            result.append(rec)
    return result



# ----------------------------------------------------------------------
# TASK 5: Hashability Classifier
# ----------------------------------------------------------------------
def is_hashable(obj: Any) -> bool:
    """
    Requirements:
    Return True if `obj` is hashable and can be safely placed in a Python set
    or used as a dict key. Return False otherwise.
    Must correctly identify that tuples containing unhashable objects (e.g. (1, [2]))
    are NOT hashable!
    """
    # TODO: Return True if hashable, False otherwise
    try:
        hash(obj)
        return True
    except:
        return False

# ======================================================================
# TEST RUNNER & ASSERTIONS
# ======================================================================
def run_tests():
    print("Running Drill 1.2 tests...\n")

    # --- Test 1: Hashability Contract ---
    k1 = GraphNodeKey("router_node", 1)
    k2 = GraphNodeKey("router_node", 1)
    k3 = GraphNodeKey("router_node", 2)
    k4 = GraphNodeKey("planner_node", 1)

    assert k1 == k2, "k1 and k2 with identical attrs must be equal"
    assert k1 != k3, "Different versions must not be equal"
    assert k1 != k4, "Different node_ids must not be equal"
    assert hash(k1) == hash(k2), "Equal objects MUST produce identical hashes!"

    lookup_map = {k1: "cached_response"}
    assert lookup_map[k2] == "cached_response", "Equal key must retrieve value from dict"

    node_set = {k1, k2, k3, k4}
    assert len(node_set) == 3, f"Set should have 3 unique keys, got {len(node_set)}"
    print("✅ Task 1 Passed: GraphNodeKey hashability contract verified.")

    # --- Test 2: Slicing Mechanics ---
    raw = [0, 1, 2, 3, 4, 5]
    assert reverse_alternate_elements(raw) == [5, 3, 1]
    assert reverse_alternate_elements([10, 20, 30, 40]) == [40, 20]
    assert reverse_alternate_elements([42]) == [42]
    assert reverse_alternate_elements([]) == []

    target = [1, 2, 3, 4, 5]
    ref_id = id(target)
    replace_middle_slice(target, 1, 4, [20, 30])
    assert target == [1, 20, 30, 5], f"Expected [1, 20, 30, 5], got {target}"
    assert id(target) == ref_id, "target_list must be modified in-place, not rebound!"
    print("✅ Task 2 Passed: Slicing & in-place slice mutation verified.")

    # --- Test 3: Starred Unpacking & Merge ---
    payload1 = ["node_01", {"action": "step"}, {"action": "log"}, "sha256_hash"]
    sender, msgs, chk = parse_agent_payload(payload1)
    assert sender == "node_01"
    assert msgs == [{"action": "step"}, {"action": "log"}]
    assert chk == "sha256_hash"

    payload2 = ["client_x", "crc32"]
    sender2, msgs2, chk2 = parse_agent_payload(payload2)
    assert sender2 == "client_x"
    assert msgs2 == []
    assert chk2 == "crc32"

    base = {"timeout": 30, "retries": 3, "debug": False}
    env = {"retries": 5, "api_key": "secret"}
    cli = {"debug": True}
    merged = merge_configurations(base, env, cli)
    assert merged == {"timeout": 30, "retries": 5, "debug": True, "api_key": "secret"}
    assert base["retries"] == 3, "base_config must not be mutated"
    print("✅ Task 3 Passed: Starred unpacking & dictionary merge verified.")

    # --- Test 4: Deduplicating Unhashable Records ---
    records = [
        {"id": 1, "text": "chunk_A"},
        {"id": 2, "text": "chunk_B"},
        {"id": 1, "text": "chunk_A"},  # Duplicate
        {"id": 3, "text": "chunk_C"},
        {"id": 2, "text": "chunk_B"},  # Duplicate
    ]
    deduped = deduplicate_records(records)
    expected = [
        {"id": 1, "text": "chunk_A"},
        {"id": 2, "text": "chunk_B"},
        {"id": 3, "text": "chunk_C"},
    ]
    assert deduped == expected, f"Deduplication failed: got {deduped}"
    print("✅ Task 4 Passed: Order-preserving unhashable deduplication verified.")

    # --- Test 5: Hashability Classifier ---
    assert is_hashable(42) is True
    assert is_hashable("antigravity") is True
    assert is_hashable((1, 2, "a")) is True
    assert is_hashable([1, 2]) is False
    assert is_hashable({"a": 1}) is False
    assert is_hashable({1, 2}) is False
    # Nested tuple with unhashable element:
    assert is_hashable((1, 2, [3, 4])) is False
    assert is_hashable((1, {"key": "val"})) is False
    print("✅ Task 5 Passed: Hashability classifier & nested tuple trap verified.")

    print("\n🎉 ALL DRILL 1.2 TESTS PASSED! Ready for Step 3: Interview Grilling.")


if __name__ == "__main__":
    run_tests()
