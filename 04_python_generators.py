"""
==============================================================================
DRILL 1.4: ITERATORS, GENERATORS, YIELD FROM & MEMORY PROFILING
==============================================================================
Target: Master the Iterator Protocol (__iter__, __next__, StopIteration),
memory-efficient lazy streaming generators, subgenerator delegation with
`yield from`, bidirectional coroutine communication via `.send()`, and
safe slicing of infinite streams with itertools.islice.

Instructions:
1. Implement each class / function marked with TODO.
2. Run this file directly with Python:
      python drills/04_python_generators.py
3. All assertions in run_tests() must PASS.
==============================================================================
"""

import itertools
from typing import Iterable, Iterator, Generator, List, Dict, Any, Tuple, Optional


# ----------------------------------------------------------------------
# TASK 1: Custom Iterator Protocol from Scratch (No `yield`)
# ----------------------------------------------------------------------
class TokenStreamIterator:
    """
    A custom iterator that streams tokens up to an optional limit without using `yield`.

    Requirements:
    1. Implement `__init__(self, tokens: List[str], max_tokens: Optional[int] = None)`:
       - Store tokens, initialize current index pointer, and calculate effective limit.
    2. Implement `__iter__(self) -> 'TokenStreamIterator'`:
       - Must return `self`.
    3. Implement `__next__(self) -> str`:
       - Return the next token in sequence.
       - If all tokens are consumed OR the number of yielded tokens reaches `max_tokens`,
         raise `StopIteration`.
    4. Must NOT use the `yield` keyword anywhere in this class.
    """
    def __init__(self, tokens: List[str], max_tokens: Optional[int] = None):
        # TODO: Implement initialization
        pass

    def __iter__(self) -> 'TokenStreamIterator':
        # TODO: Implement iterator protocol __iter__
        pass

    def __next__(self) -> str:
        # TODO: Implement iterator protocol __next__
        pass


# ----------------------------------------------------------------------
# TASK 2: Lazy Chunking / Batching Generator for Large Datasets
# ----------------------------------------------------------------------
def batch_stream_records(stream: Iterable[Any], batch_size: int) -> Iterator[List[Any]]:
    """
    In RAG ingestion and model fine-tuning, datasets can be tens of gigabytes.
    Materializing the entire stream as a list crashes memory.

    Requirements:
    1. Accept an arbitrary iterable `stream` and an integer `batch_size` (batch_size >= 1).
    2. Yield batches (lists) of size `batch_size` on the fly.
    3. The final batch may contain fewer than `batch_size` items if elements run out.
    4. CRITICAL: Do NOT convert `stream` to a list (`list(stream)`); process elements
       lazily as they arrive.
    5. If `stream` is empty, yield nothing.
    """
    # TODO: Implement memory-efficient batching generator
    pass


# ----------------------------------------------------------------------
# TASK 3: Subgenerator Delegation with `yield from` & Return Value Capture
# ----------------------------------------------------------------------
def process_document_subgen(doc_id: str, chunks: List[str]) -> Generator[str, None, Dict[str, Any]]:
    """
    Subgenerator that processes chunks for a single document.

    Requirements:
    1. For each chunk (0-indexed i), yield the string:
       f"DOC-{doc_id}: chunk_{i}"
    2. After all chunks are yielded, RETURN a dictionary with:
       {"doc_id": doc_id, "total_chunks": len(chunks), "status": "COMPLETED"}
       (Note: generators return values via `return <val>`, which embeds in StopIteration).
    """
    # TODO: Implement subgenerator yielding chunk messages and returning summary dict
    pass


def agent_pipeline_coordinator(
    docs: List[Tuple[str, List[str]]]
) -> Generator[str, None, List[Dict[str, Any]]]:
    """
    Master generator coordinating document processing across multiple documents.

    Requirements:
    1. Iterate over each (doc_id, chunks) pair in `docs`.
    2. Delegate chunk streaming to `process_document_subgen(doc_id, chunks)`
       using the `yield from` expression:
           summary = yield from process_document_subgen(doc_id, chunks)
    3. Collect each returned `summary` dictionary into a list.
    4. After all documents are processed, RETURN the list of summary dictionaries.
    """
    # TODO: Implement delegating coordinator generator using `yield from`
    pass


# ----------------------------------------------------------------------
# TASK 4: Bidirectional Coroutine with `.send()` and Reset Signal
# ----------------------------------------------------------------------
def token_telemetry_coroutine() -> Generator[int, Optional[str], None]:
    """
    A generator-based coroutine tracking character count in a streaming LLM response.

    Requirements:
    1. Initialize `total_chars = 0`.
    2. When first primed (via `next()` or `.send(None)`), it yields the initial `total_chars` (0).
    3. In an infinite loop:
       - Receive `signal = yield total_chars`.
       - If `signal == "RESET"`:
           reset `total_chars = 0`.
       - Else if `signal` is a string:
           add `len(signal)` to `total_chars`.
       - Else if `signal is None`:
           keep `total_chars` unchanged.
       - Then loop back and yield the updated `total_chars`.
    """
    # TODO: Implement bidirectional coroutine responding to .send()
    pass


# ----------------------------------------------------------------------
# TASK 5: Infinite Stream & Window Slicing with `itertools.islice`
# ----------------------------------------------------------------------
def infinite_heartbeat_stream(start_id: int = 1) -> Generator[Dict[str, Any], None, None]:
    """
    An infinite generator producing telemetry heartbeat pings.

    Requirements:
    1. Starting at `current_id = start_id`, loop infinitely:
       - Yield {"id": current_id, "status": "ALIVE"}
       - Increment `current_id` by 1.
    """
    # TODO: Implement infinite heartbeat generator
    pass


def safe_stream_window(stream: Iterator[Any], window_size: int) -> List[Any]:
    """
    Safely consume a finite slice of an infinite (or finite) stream without hanging.

    Requirements:
    1. Use `itertools.islice` to extract at most `window_size` items from `stream`.
    2. Return the extracted items as a Python list.
    3. Because `stream` is an iterator, subsequent calls to `safe_stream_window`
       on the same stream instance MUST advance the stream pointer sequentially.
    """
    # TODO: Implement safe window slicing using itertools.islice
    pass


# ======================================================================
# TEST RUNNER & ASSERTIONS
# ======================================================================
def run_tests():
    print("Running Drill 1.4 tests...\n")

    # --- Test 1: Custom Iterator Protocol ---
    tokens = ["DeepSeek", "Gemini", "Claude", "GPT-4", "Llama-3"]
    # Test full iteration
    iter1 = TokenStreamIterator(tokens)
    assert iter(iter1) is iter1, "__iter__() must return self"
    assert next(iter1) == "DeepSeek"
    assert next(iter1) == "Gemini"
    assert list(iter1) == ["Claude", "GPT-4", "Llama-3"]
    try:
        next(iter1)
        assert False, "Should have raised StopIteration"
    except StopIteration:
        pass

    # Test with max_tokens limit
    iter2 = TokenStreamIterator(tokens, max_tokens=2)
    result2 = list(iter2)
    assert result2 == ["DeepSeek", "Gemini"], f"Expected 2 tokens, got {result2}"
    print("✅ Task 1 Passed: Custom TokenStreamIterator verified.")

    # --- Test 2: Lazy Chunking Generator ---
    data = list(range(10))
    batches = list(batch_stream_records(data, batch_size=3))
    assert batches == [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]], f"Got {batches}"

    # Test empty stream
    empty_batches = list(batch_stream_records([], batch_size=4))
    assert empty_batches == []

    # Test with generator input (verifying it doesn't require len or indexable)
    gen_input = (x * 2 for x in range(5))
    gen_batches = list(batch_stream_records(gen_input, batch_size=2))
    assert gen_batches == [[0, 2], [4, 6], [8]]
    print("✅ Task 2 Passed: Lazy batch_stream_records verified.")

    # --- Test 3: Subgenerator Delegation with yield from ---
    sample_docs = [
        ("A", ["chunk_0", "chunk_1"]),
        ("B", ["chunk_0"]),
    ]
    coordinator = agent_pipeline_coordinator(sample_docs)

    # Collect yielded messages
    yielded_messages = []
    try:
        while True:
            msg = next(coordinator)
            yielded_messages.append(msg)
    except StopIteration as e:
        # The return value of the coordinator is stored in e.value!
        summaries = e.value

    assert yielded_messages == [
        "DOC-A: chunk_0",
        "DOC-A: chunk_1",
        "DOC-B: chunk_0"
    ], f"Unexpected yielded messages: {yielded_messages}"

    assert summaries == [
        {"doc_id": "A", "total_chunks": 2, "status": "COMPLETED"},
        {"doc_id": "B", "total_chunks": 1, "status": "COMPLETED"}
    ], f"Unexpected summaries returned: {summaries}"
    print("✅ Task 3 Passed: Subgenerator delegation and return capture verified.")

    # --- Test 4: Coroutine Communication via .send() ---
    coro = token_telemetry_coroutine()
    # Priming:
    initial_count = next(coro)
    assert initial_count == 0, f"Expected initial count 0, got {initial_count}"

    # Sending tokens
    c1 = coro.send("Hello")
    assert c1 == 5  # len("Hello") = 5

    c2 = coro.send(" World!")
    assert c2 == 12  # 5 + 7 = 12

    # Sending None (no change)
    c3 = coro.send(None)
    assert c3 == 12

    # Reset signal
    c4 = coro.send("RESET")
    assert c4 == 0

    c5 = coro.send("AI")
    assert c5 == 2
    coro.close()
    print("✅ Task 4 Passed: Bidirectional token_telemetry_coroutine verified.")

    # --- Test 5: Infinite Generator & Safe Slicing with islice ---
    stream = infinite_heartbeat_stream(start_id=100)
    w1 = safe_stream_window(stream, window_size=3)
    assert w1 == [
        {"id": 100, "status": "ALIVE"},
        {"id": 101, "status": "ALIVE"},
        {"id": 102, "status": "ALIVE"}
    ], f"Window 1 mismatch: {w1}"

    # Verify sequential pointer advancement on the same stream:
    w2 = safe_stream_window(stream, window_size=2)
    assert w2 == [
        {"id": 103, "status": "ALIVE"},
        {"id": 104, "status": "ALIVE"}
    ], f"Window 2 mismatch: {w2}"
    print("✅ Task 5 Passed: Infinite stream and safe islice windowing verified.")

    print("\n🎉 ALL DRILL 1.4 TESTS PASSED! Ready for Step 3: Interview Grilling.")


if __name__ == "__main__":
    run_tests()
