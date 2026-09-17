# Practice problems with stacks and queues

Exercise 3 (reverse a stack) is implemented, in `src/linked_structures/reverse_stack.py`,
tested in `tests/test_reverse_stack.py`. Exercises 4 and 5 are strategies only,
per the assignment (only one implementation is required).

## Exercise 3: reverse a stack (implemented)

Draining a stack into a queue and back reverses it, using one auxiliary
structure and two passes:

1. While the stack is not empty, pop a value and enqueue it. Popping yields
   the stack's values top to bottom, in order, and a queue relays that same
   order unchanged since FIFO does not reorder anything.
2. While the queue is not empty, dequeue a value and push it back onto the
   stack. Pushing a sequence onto an empty stack always puts the last value on
   top, so pushing that same top-to-bottom order back reverses it: what was on
   top is now on the bottom, and vice versa.

O(n) time (two linear passes), O(n) auxiliary space for the queue.

## Exercise 4: valid parentheses

Strategy: scan the string once, using a stack of the open brackets seen so
far.

- On an opening bracket (`(`, `[`, `{`), push it.
- On a closing bracket, if the stack is empty, the string is invalid (a close
  with nothing open). Otherwise pop the stack and check the popped bracket is
  the matching open type for this close (a lookup table from close to its
  matching open makes this a single comparison, e.g. `)` maps to `(`). If it
  doesn't match, the string is invalid.
- Any other character is ignored, or is itself invalid, depending on the
  exact problem statement.
- After the scan, the string is valid only if every open bracket found a
  match and the stack is empty at the end (no unmatched opens left over).

One pass, O(n) time, O(n) worst-case space for the stack (all opens, no
closes).

## Exercise 5: copy stack (one queue as auxiliary storage)

Source: University of Washington CSE122. Goal: given a stack, return a new
stack holding the same values in the same order, using one queue as the only
extra storage, leaving the original stack the way it started.

The reverse-stack trick from Exercise 3 is the building block, and the key
fact worth being explicit about: a single pass through a queue does not
restore a stack to its original order, it reverses it, for the same reason
Exercise 3 works. So restoring the original order needs that reversal applied
twice.

Strategy, reusing one `Queue` instance across two sequential phases:

1. **Phase A, reverse the original stack.** Run the Exercise 3 procedure on
   the input stack using the queue: drain it into the queue, then drain the
   queue back into the stack. The stack now holds its values in reverse
   order.
2. **Phase B, un-reverse while building the copy.** Drain the now-reversed
   stack into the (now empty) queue again. Then, dequeuing one value at a
   time, push each value onto *both* the original stack and the new copy
   stack. Pushing that dequeue order onto an empty stack reverses it again,
   which cancels Phase A's reversal, so the original stack ends up back in
   its original order, and the copy, built from that same dequeue order,
   ends up in that same original order too.

Net effect: two reversals cancel out, the original stack is unchanged, and
the copy matches it, using one queue reused twice and no second stack.
O(n) time (four linear passes total), O(n) auxiliary space.

## Optional problems

Not attempted (optional, per the assignment): splice stack, and the linked
LeetCode stack/queue problems. Worth a look if there's time before this is
due, not required for the rubric.
