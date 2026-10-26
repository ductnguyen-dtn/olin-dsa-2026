# Policy iteration vs. value iteration

## The problem: a Markov Decision Process

An MDP is a tuple `(S, A, P, R, gamma)`: states `S`, actions `A`, a
transition model `P(s' | s, a)` giving the probability of landing in `s'`
after taking action `a` in state `s`, a reward function `R(s, a, s')`,
and a discount factor `gamma in [0, 1)` controlling how much future
reward is worth relative to immediate reward. Both algorithms here assume
the model (`P` and `R`) is fully known. That assumption is exactly what
gets dropped in the PPO section below.

A **policy** `pi` maps states to actions. The **value function** `V^pi(s)`
is the expected discounted sum of future reward starting from `s` and
following `pi` forever after:

```
V^pi(s) = E[ R_t + gamma*R_{t+1} + gamma^2*R_{t+2} + ... | s_0 = s, pi ]
```

## The Bellman equation

`V^pi` can be written recursively in terms of itself one step later. This
is the Bellman expectation equation:

```
V^pi(s) = sum_{s'} P(s' | s, pi(s)) * [ R(s, pi(s), s') + gamma * V^pi(s') ]
```

The optimal value function `V*` satisfies the Bellman optimality
equation, which replaces "follow the fixed policy's action" with "take
whichever action is best":

```
V*(s) = max_a sum_{s'} P(s' | s, a) * [ R(s, a, s') + gamma * V*(s') ]
```

Both algorithms solve this second equation for `V*`. `q_value()` in
`dp.py` computes the inner `sum_{s'} P(...) * [...]` term for one action,
and taking `max_a` over it is the Bellman optimality backup used in
`value_iteration`.

## Value iteration

Apply the Bellman optimality backup to every state, repeatedly, until the
values stop changing:

```
V_{k+1}(s) <- max_a sum_{s'} P(s'|s,a) [ R(s,a,s') + gamma * V_k(s') ]
```

This update is a contraction mapping in the max-norm with contraction
factor `gamma`. Each full sweep shrinks the largest possible error between
`V_k` and `V*` by at least a factor of `gamma`. A contraction mapping
converges to its unique fixed point under repeated application (this is
Banach's fixed-point theorem), so `V_k` approaches `V*` as `k` grows, and
in practice the loop stops once the largest per-state change (`delta` in
`dp.py`) drops below a small threshold `theta`.

## Policy iteration

Alternate two steps until the policy stops changing:

1. **Policy evaluation**: compute `V^pi` for the current policy `pi`, by
   repeatedly applying the Bellman expectation backup. There's no `max_a`
   here, since the policy already picked the action.
2. **Policy improvement**: set `pi'(s)` to whichever action maximizes
   `sum_{s'} P(s'|s,a) [R(s,a,s') + gamma*V^pi(s')]`, i.e. act greedily
   with respect to the value function just computed.

Why this converges: the policy improvement theorem says that if `pi'` is
greedy with respect to `V^pi`, then `V^{pi'}(s) >= V^pi(s)` for every
state, with strict improvement somewhere unless `pi` was already optimal.
So each outer loop either strictly improves the policy or leaves it
unchanged. There are only finitely many deterministic policies on a
finite MDP (`|A|^|S|` of them), and a process that never gets worse and
never repeats a policy has to terminate, landing on a policy that is its
own greedy improvement. A policy that is its own greedy improvement
satisfies the Bellman optimality equation by construction, which makes it
`pi*`. `test_policy_iteration_needs_no_more_outer_iterations_than_states`
in `tests/test_dp.py` checks this termination bound directly.

## Correctness

`tests/test_dp.py::test_hand_verified_corridor` is a 1x3 deterministic
corridor worked out by hand, shown in the test's docstring: with
step_reward=-1, a goal paying 0, and gamma=0.9, `V*(0,1) = 0` and
`V*(0,0) = -1` follow directly from the Bellman equation, and both
algorithms reproduce these exact numbers. `test_value_and_policy_iteration_agree`
cross-checks both algorithms against each other, not just against a hand
calculation, on four larger stochastic gridworlds, confirming the value
functions match to within `1e-3` and that any disagreement between the two
policies is a genuine tie in Q-value rather than a bug.
`test_optimal_policy_routes_around_a_pit` checks that the optimal policy
actually avoids a modeled hazard when a same-cost route around it exists.

## Benchmark: iterations and runtime

Real run, `python -m deep_dive.benchmark`
(`benchmark_data/mdp_results.csv`, 3 trials per configuration, means
shown, gamma=0.95, theta=1e-6; plotted in `benchmark_data/size_sweep.png`):

**Grid size sweep** (reward_setup fixed: step_reward=-0.04, noise=0.2):

| n (n x n grid) | VI iterations | VI time (s) | PI iterations | PI time (s) | PI / VI time |
|---|---|---|---|---|---|
| 4  | 26  | 0.0021 | 5  | 0.0117 | 5.6x  |
| 8  | 39  | 0.0103 | 11 | 0.1176 | 11.5x |
| 16 | 61  | 0.0662 | 22 | 1.0690 | 16.2x |
| 32 | 101 | 0.4535 | 45 | 9.6867 | 21.4x |

**Reward/noise setup sweep** (grid fixed at 16x16):

| setup | step_reward | noise | VI iterations | VI time (s) | PI iterations | PI time (s) |
|---|---|---|---|---|---|---|
| standard    | &minus;0.04 | 0.2 | 61 | 0.0669 | 22 | 1.0752 |
| harsh_steps | &minus;1.0  | 0.2 | 60 | 0.0655 | 22 | 1.3505 |
| no_noise    | &minus;0.04 | 0.0 | 31 | 0.0190 | 31 | 1.1124 |
| high_noise  | &minus;0.04 | 0.4 | 87 | 0.0951 | 21 | 1.1053 |

The size sweep shows a real tradeoff, but not the one I expected walking
in. Policy iteration does converge in far fewer outer iterations than
value iteration at every size (45 vs. 101 at n=32), so the textbook claim
holds up. What I didn't expect is that policy iteration is still the
slower algorithm overall, by a growing margin: 5.6x slower at n=4, 21.4x
slower by n=32. The code explains why. `policy_iteration` calls
`policy_evaluation` once per outer loop, and that single call runs its own
inner loop of Bellman expectation backups all the way to convergence, so
every outer iteration of policy iteration does roughly as much work as an
entire run of value iteration. At n=32 that works out to about 0.215
seconds per policy-iteration outer step against about 0.0045 seconds per
value-iteration sweep, a gap of roughly 48x per iteration that swamps
policy iteration's 2.2x advantage in iteration count. And that gap gets
worse with grid size because the inner evaluation's cost scales with the
number of states, and it's being paid on every single outer iteration.
This is the same reason "modified policy iteration" exists in the
literature: in practice people truncate the inner evaluation loop to a
handful of sweeps instead of running it to full convergence every time,
which is a direct fix for exactly this cost.

The reward/noise sweep separates two things I'd been lumping together in
my head: how far values have to swing, and how hard the problem actually
is. Noise clearly drives value iteration's iteration count, going from 31
iterations with no noise up to 87 at noise=0.4, nearly tripling. But
making every step 25 times more costly (step_reward -0.04 to -1.0, the
"harsh_steps" row) barely moves it at all, 61 iterations down to 60. That
makes sense once you think about what's actually being measured: the stop
condition checks how much values change between sweeps, and that's set by
gamma and by how far value information has to propagate through the
transition structure, not by how big the rewards themselves are.

Policy iteration's outer-iteration count doesn't follow the same pattern.
It barely moves across the noise levels (22, 22, 21), but the no-noise
setup needed the most outer iterations of any row, 31. My best guess is
that a deterministic gridworld gives each policy-improvement step less to
work with: there's no probability-weighted averaging over outcomes to
smooth things out, so more rounds of improvement are needed before the
policy settles. I don't have a proof of this, just the pattern in the
data, which is itself a reminder that the two algorithms don't respond to
the same knobs the same way.

## Connection to PPO

Policy iteration and value iteration both assume a fully known model:
exact transition probabilities `P(s'|s,a)` and exact rewards `R(s,a,s')`
for every state-action pair, with a state space small enough to store a
value function as a table and sweep over every entry. None of that holds
for the robots I actually run PPO on, the SpotMicro quadruped and the G1
humanoid, both in Isaac Lab. The state space is continuous rather than a
finite grid: joint angles, velocities, IMU readings. There's no table to
sweep over. The transition model isn't known in closed form either.
Nobody has written down `P(s' | s, a)` for "this quadruped's exact
dynamics given this joint torque command"; it's whatever the physics
simulator, or the real world, produces when the action is actually taken.
And the reward is only observed by taking the action, not computed ahead
of time the way `GridWorld.transitions()` computes it here.

PPO is built for that setting. It's model-free: `V` and `pi` are both
neural networks that generalize across the continuous state space instead
of storing one table entry per state. Instead of a Bellman backup that
sums over a known `P(s'|s,a)`, PPO estimates how good an action was from
sampled rollouts, actually simulating the robot, observing what reward
and next state resulted, and using that sample (averaged over many
parallel environments) in place of the exact expectation that policy
iteration computes directly. And instead of the exact greedy improvement
step, taking the argmax over a fully known one-step lookahead, PPO takes a
small, clipped gradient step on the policy network. The clipping matters
because a large step based on noisy, sampled value estimates can make the
policy worse instead of better; it's PPO's stand-in for the guarantee
policy iteration gets for free from the policy improvement theorem, that
an update can never hurt.

So the trade PPO makes is this: give up the exactness and the convergence
guarantees that come from having a fully known, enumerable model, in
exchange for being able to scale to state spaces where no such model
could ever be written down or stored as a table. Working through value
iteration and policy iteration here, in a setting where that trade isn't
necessary and the exact algorithm is actually available to run, is what
let me see specifically which assumption PPO is giving up and why, rather
than treating PPO's update rule as a black box I just happen to call every
training run.

## AI assistance

The code, its docstrings and inline comments, and this writeup were
produced with the help of Claude (Anthropic), under my direction and
review, following the project proposal and self-assessment rubric
([`proposal.md`](proposal.md)) written for this assignment.
