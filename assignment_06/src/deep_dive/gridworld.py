"""A gridworld Markov Decision Process: the small, fully-known-model MDP that
policy iteration and value iteration are classically run on.

State = a non-wall (row, col) cell. Action = one of up/down/left/right.
Transitions are stochastic: with probability `1 - noise` the agent moves in
the intended direction; the remaining `noise` probability is split evenly
between the two directions perpendicular to it (the classic "slippery floor"
gridworld from Russell & Norvig / Sutton & Barto). Moving into a wall or off
the edge of the grid leaves the agent in place for that outcome. Terminal
cells (goals, pits) end the episode and have no outgoing actions; the reward
for reaching one is paid on the transition that enters it, not per turn spent
sitting in it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

State = tuple[int, int]
Action = str

ACTIONS: tuple[Action, ...] = ("up", "down", "left", "right")

_DELTA: dict[Action, tuple[int, int]] = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}

# The two directions perpendicular to each action, where a "slip" goes.
_PERPENDICULAR: dict[Action, tuple[Action, Action]] = {
    "up": ("left", "right"),
    "down": ("left", "right"),
    "left": ("up", "down"),
    "right": ("up", "down"),
}


@dataclass(frozen=True)
class GridWorld:
    rows: int
    cols: int
    terminals: dict[State, float]
    walls: frozenset[State] = field(default_factory=frozenset)
    step_reward: float = -0.04
    noise: float = 0.2

    def __post_init__(self) -> None:
        if not (0.0 <= self.noise <= 1.0):
            raise ValueError(f"noise must be in [0, 1], got {self.noise}")
        for s in self.terminals:
            if s in self.walls:
                raise ValueError(f"terminal state {s} cannot also be a wall")

    def in_bounds(self, s: State) -> bool:
        r, c = s
        return 0 <= r < self.rows and 0 <= c < self.cols

    def states(self) -> list[State]:
        return [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if (r, c) not in self.walls
        ]

    def is_terminal(self, s: State) -> bool:
        return s in self.terminals

    def actions(self, s: State) -> tuple[Action, ...]:
        return () if self.is_terminal(s) else ACTIONS

    def _step(self, s: State, a: Action) -> State:
        """Where `a` takes you from `s`, ignoring noise: bounce back to `s`
        if that would leave the grid or hit a wall."""
        dr, dc = _DELTA[a]
        next_s = (s[0] + dr, s[1] + dc)
        if not self.in_bounds(next_s) or next_s in self.walls:
            return s
        return next_s

    def transitions(self, s: State, a: Action) -> list[tuple[float, State, float]]:
        """All (probability, next_state, reward) outcomes of taking action
        `a` in state `s`. Probabilities sum to 1, over however many outcome
        entries that takes. Duplicate next_states are not merged, since the
        expectation sum used in the Bellman backup is correct either way."""
        if self.is_terminal(s):
            return []

        perp_a, perp_b = _PERPENDICULAR[a]
        outcomes: list[tuple[float, Action]]
        if self.noise == 0.0:
            outcomes = [(1.0, a)]
        else:
            outcomes = [
                (1.0 - self.noise, a),
                (self.noise / 2, perp_a),
                (self.noise / 2, perp_b),
            ]

        results: list[tuple[float, State, float]] = []
        for prob, direction in outcomes:
            if prob == 0.0:
                continue
            next_s = self._step(s, direction)
            reward = self.terminals.get(next_s, self.step_reward)
            results.append((prob, next_s, reward))
        return results
