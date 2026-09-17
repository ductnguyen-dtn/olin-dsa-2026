# Olin DSA 2026: Assignment 2, Linked Data Structures

Language: Python with type hints (`mypy --strict`). Python has no KDoc; every
public class and function has a docstring in its place, plus inline comments
on the parts of the linked-list pointer logic that aren't obvious from the
code alone.

## Contents

| Path | Component |
|---|---|
| [`src/linked_structures/doubly_linked_list.py`](src/linked_structures/doubly_linked_list.py) | Generic doubly linked list: push/pop/peek at both ends, all O(1) |
| [`src/linked_structures/stack.py`](src/linked_structures/stack.py) | Stack ADT, built on the linked list |
| [`src/linked_structures/fifo_queue.py`](src/linked_structures/fifo_queue.py) | Queue ADT, built on the linked list |
| [`src/linked_structures/reverse_stack.py`](src/linked_structures/reverse_stack.py) | Practice problem 3: reverse a stack with one auxiliary queue |
| [`src/linked_structures/valid_parentheses.py`](src/linked_structures/valid_parentheses.py) | Practice problem 4: valid parentheses |
| [`src/linked_structures/copy_stack.py`](src/linked_structures/copy_stack.py) | Practice problem 5: copy a stack using one queue |
| [`tests/`](tests/) | pytest suite (243 tests), including randomized cross-checks against `collections.deque` / `list` |
| [`docs/practice_problems.md`](docs/practice_problems.md) | How and why each practice-problem solution works |

The assignment only requires implementing one of the three practice problems
(with a strategy for the other two); all three are implemented here.

## Running the checks

```bash
make venv     # one-time: create .venv, install pytest + mypy
make check    # pytest + mypy
```

> This machine sources ROS 2 Jazzy in `.bashrc`, which puts `/opt/ros` on
> `PYTHONPATH` and breaks bare `pytest`. The Makefile runs everything in a
> clean environment; to run tools by hand use
> `env -u PYTHONPATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest`.

## Design notes

`Stack` and `Queue` are adapters over `DoublyLinkedList`, not separate
implementations: `Stack.push`/`pop` call `push_front`/`pop_front` (top = front
of the list), and `Queue.enqueue`/`dequeue` call `push_back`/`pop_front`
(enqueue at the back, dequeue from the front). Every method on both is a
one-liner, as the assignment asks, since the linked list already does the
real work.

Like the assignment's own Kotlin interface, `pop`/`peek`/`dequeue` return
`None` on an empty structure rather than raising, so `None` can't be told
apart from "a stored value that happens to be `None`". That's a limitation
inherited from the required interface, not something this port tries to work
around.

Tests for the three data structures are randomized: a sequence of random
operations is run against both the implementation and a Python built-in with
matching semantics (`collections.deque` for the linked list and the queue, a
plain `list` for the stack), asserting they agree at every step. `copy_stack`
has a similar randomized cross-check against the input it was built from.
