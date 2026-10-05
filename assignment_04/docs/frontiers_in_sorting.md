# Frontiers in sorting: AlphaDev (extra credit)

How I learned about this: Google DeepMind's own write-up,
["AlphaDev discovers faster sorting algorithms"](https://deepmind.google/blog/alphadev-discovers-faster-sorting-algorithms/),
cross-checked against the peer-reviewed paper it summarizes, Mankowitz et al.,
["Faster sorting algorithms discovered using deep reinforcement learning"](https://www.nature.com/articles/s41586-023-06004-9),
*Nature* 618, 2023.

## The problem setting

The class of problem this course covers (merge sort, quick sort, heap sort,
and the rest) is *comparison-based* sorting of an arbitrary-length list, where
the Θ(n log n) lower bound from `docs/complexity_analysis.md` is the speed
limit no comparison-based algorithm can beat. AlphaDev targets something
narrower but surprisingly high-value: hand-optimizing the assembly-level
routines used to sort *very short, fixed-length* sequences, specifically 3, 4,
and 5 elements. Those tiny sorts are not usually what a programmer calls
directly. They are the base case that a general-purpose sort (like this
assignment's merge or quick sort) switches to once it has recursively split
its input down to a handful of elements, where the overhead of further
recursion outweighs just sorting the small piece directly. Because every call
to a general sort on real hardware bottoms out in one of these tiny sorts,
and general sorts are among the most frequently executed routines in all of
software, a faster 3-5 element sort has an outsized, multiplied effect: the
DeepMind write-up notes these routines are invoked trillions of times a day.

## What AlphaDev did differently

The previous state of the art for small fixed-size sorts was already the
product of decades of expert, manual optimization. AlphaDev did not try to
design a new sorting *algorithm* in the way this assignment's four are
algorithms (a strategy expressed at the level of "compare these, then
recurse"). Instead, it searched directly in the space of CPU assembly
instructions. The DeepMind team framed finding a sort routine as a
single-player game, called AssemblyGame: at each turn, an RL agent (built on
the AlphaZero game-playing approach also behind AlphaGo and AlphaZero for
chess) observes the current partial sequence of assembly instructions and the
CPU's state, and chooses the next instruction to append, with the eventual
reward based on whether the finished sequence correctly sorts every input and
how few instructions and clock cycles it took.

Searching at this level let AlphaDev find optimizations no one sorting
*algorithm* description would capture, because they are about how comparisons
and swaps get compiled to hardware instructions, not about the comparison
structure itself. The paper's headline example is what the DeepMind
write-up calls an "AlphaDev swap move": for sorting three values, the
conventional approach computes a minimum through a sequence of comparisons
that functionally behaves like a three-way operation; AlphaDev found it could
get the same correct result from an equivalent two-term operation, cutting
out redundant instructions. It is described as a non-obvious shortcut, in the
same spirit as AlphaGo's famous "Move 37": something a search process found
that human experts had not, even after this exact problem had been optimized
by hand for decades.

## Why it's significant

Two things make this result land differently from "found a slightly faster
constant factor," which on its own would not be very notable:

1. **It shipped.** The discovered instruction sequences were reverse-engineered
   back into C++ and merged into LLVM's libc++ standard library, the actual
   sorting implementation behind `std::sort` for a widely used C++ standard
   library. It was the first change made to that part of the library in over
   a decade, and (per the DeepMind write-up) the first component of a major
   standard library ever contributed by a reinforcement learning system. Any
   C++ program built against that libc++ version got faster small-sequence
   sorts for free.
2. **The size of the win, and where it shows up.** DeepMind reports up to 70%
   faster for the short, 3-5 element sequences AlphaDev specifically targeted,
   and about 1.7% faster even for sequences beyond 250,000 elements, since any
   general-purpose sort recursing down to small base cases benefits every time
   it hits one. 1.7% sounds small next to 70%, but it is a 1.7% speedup on
   one of the single most-executed routines in computing, applied without any
   programmer needing to change a line of their own code.

This is also a concrete, shipped counterexample to the idea that sorting is a
"solved problem" once you know Θ(n log n) is optimal for comparisons: the
constant factor, and the actual machine instructions realizing an algorithm,
were still worth searching over, by a method quite different from the
analysis-by-hand this assignment's four algorithms were designed with.

---

*AI assistance: this writeup was produced with the help of Claude (Anthropic), under my direction and review.*
