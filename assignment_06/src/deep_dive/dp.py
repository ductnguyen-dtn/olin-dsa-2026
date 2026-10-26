"""Value iteration and policy iteration: the two classic dynamic-programming
algorithms for solving a Markov Decision Process with a fully known model
(transition probabilities and rewards), via the Bellman equation.

Both return (V, policy, iterations): the converged value function, the
converged greedy policy, and how many outer-loop iterations it took. That
iteration count is the quantity the benchmark in `benchmark.py` compares
between them.
"""

from __future__ import annotations

from deep_dive.gridworld import Action, GridWorld, State


def q_value(mdp: GridWorld, s: State, a: Action, gamma: float, V: dict[State, float]) -> float:
    """Expected discounted return of taking action `a` in state `s`, then
    following V thereafter. This is the right-hand side of the Bellman
    equation for a single (state, action) pair."""
    return sum(prob * (reward + gamma * V[next_s]) for prob, next_s, reward in mdp.transitions(s, a))


def extract_policy(mdp: GridWorld, V: dict[State, float], gamma: float) -> dict[State, Action]:
    """Greedy policy w.r.t. V: in each state, the action with the highest
    Q-value under V."""
    policy: dict[State, Action] = {}
    for s in mdp.states():
        if mdp.is_terminal(s):
            continue
        policy[s] = max(mdp.actions(s), key=lambda a: q_value(mdp, s, a, gamma, V))
    return policy


def value_iteration(
    mdp: GridWorld,
    gamma: float,
    theta: float = 1e-8,
    max_iterations: int = 100_000,
) -> tuple[dict[State, float], dict[State, Action], int]:
    """Repeatedly apply the Bellman optimality backup to every state at once
    until the largest change in any state's value drops below `theta`."""
    V: dict[State, float] = {s: 0.0 for s in mdp.states()}

    iterations = 0
    for _ in range(max_iterations):
        iterations += 1
        new_V = dict(V)
        delta = 0.0
        for s in mdp.states():
            if mdp.is_terminal(s):
                continue
            new_V[s] = max(q_value(mdp, s, a, gamma, V) for a in mdp.actions(s))
            delta = max(delta, abs(new_V[s] - V[s]))
        V = new_V
        if delta < theta:
            break

    policy = extract_policy(mdp, V, gamma)
    return V, policy, iterations


def policy_evaluation(
    mdp: GridWorld,
    policy: dict[State, Action],
    gamma: float,
    theta: float = 1e-8,
    max_iterations: int = 100_000,
) -> dict[State, float]:
    """Compute V^pi for a fixed policy pi, by repeatedly applying the
    Bellman expectation backup (no max over actions, since the policy
    already picked the action) until it converges."""
    V: dict[State, float] = {s: 0.0 for s in mdp.states()}

    for _ in range(max_iterations):
        new_V = dict(V)
        delta = 0.0
        for s in mdp.states():
            if mdp.is_terminal(s):
                continue
            new_V[s] = q_value(mdp, s, policy[s], gamma, V)
            delta = max(delta, abs(new_V[s] - V[s]))
        V = new_V
        if delta < theta:
            break

    return V


def policy_iteration(
    mdp: GridWorld,
    gamma: float,
    theta: float = 1e-8,
    max_iterations: int = 10_000,
) -> tuple[dict[State, float], dict[State, Action], int]:
    """Alternate full policy evaluation with greedy policy improvement until
    the policy stops changing. Each outer loop iteration is one
    evaluate-then-improve cycle, which is strictly more expensive per
    iteration than value iteration's single backup sweep, but it typically
    needs far fewer of them, because a full evaluation propagates
    information across the whole state space in one shot instead of one
    Bellman backup at a time."""
    policy: dict[State, Action] = {s: mdp.actions(s)[0] for s in mdp.states() if not mdp.is_terminal(s)}

    V: dict[State, float] = {}
    iterations = 0
    for _ in range(max_iterations):
        iterations += 1
        V = policy_evaluation(mdp, policy, gamma, theta)
        new_policy = extract_policy(mdp, V, gamma)
        policy_stable = new_policy == policy
        policy = new_policy
        if policy_stable:
            break

    return V, policy, iterations
