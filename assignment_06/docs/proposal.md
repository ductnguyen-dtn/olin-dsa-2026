# Project proposal

For my Deep Dive, I want to implement and compare policy iteration and
value iteration, the two classic dynamic programming algorithms for
solving Markov Decision Processes. Policy iteration works by alternating
between evaluating how good your current policy is and then improving it,
and it eventually converges to the optimal policy. What makes this
interesting to me is that it's basically the tabular ancestor of PPO, the
algorithm I'm already using to train locomotion policies for my G1
humanoid and SpotMicro quadruped in Isaac Lab. I want to actually
understand the classical version before I keep tweaking the deep RL
version I'm running on real robots. My plan is to build a small gridworld
MDP (states, actions, a transition model, rewards), implement both
algorithms from scratch, and check that they both converge to the same
optimal policy, including on at least one gridworld simple enough that I
can verify the answer by hand. Then I'll benchmark the two against each
other, looking at how many iterations each needs and how long they
actually take across different gridworld sizes and reward setups. I'll
wrap it up with a writeup covering the Bellman equation, why policy
iteration actually converges, what the benchmarks showed, and a section
tying it back to PPO, basically explaining why PPO gives up the "fully
known model" assumption that policy iteration relies on, and why that
tradeoff is exactly what lets it scale to the continuous, high dimensional
state spaces my actual robots live in.

Time-wise I'm budgeting about an hour to review the MDP and convergence
theory, an hour and a half each to implement value iteration and policy
iteration, an hour for unit tests on a few gridworlds, an hour for the
benchmark code and actually running it, an hour and a half for the
writeup, and half an hour of buffer, which comes out to around eight
hours.

## Self-assessment rubric

**A-level work:** both algorithms are correctly implemented and agree
with each other and with a hand-checked optimal policy on at least one
simple gridworld; there's real benchmark data comparing iterations and
runtime across multiple gridworld sizes and reward setups; the writeup
actually connects this back to why something like PPO is necessary for my
real robot projects instead of just gesturing at it; and the code is
documented and tested.

**B-level work:** both algorithms working and benchmarked against each
other with real data, and a solid explanation of the Bellman equation and
convergence, but the PPO connection is thinner or more surface-level.

**C-level work:** policy iteration and/or value iteration implemented and
passing basic correctness checks, but no real benchmark comparing them,
or the PPO connection being missing or pretty hand-wavy.
