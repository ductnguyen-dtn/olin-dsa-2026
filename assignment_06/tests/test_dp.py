import pytest

from deep_dive.dp import policy_iteration, value_iteration
from deep_dive.gridworld import GridWorld


def test_hand_verified_corridor() -> None:
    """A 1x3 deterministic corridor: (0,0) -> (0,1) -> (0,2)=goal.
    step_reward=-1 per move, goal pays 0 (just stops the bleeding), gamma=0.9,
    no noise. Worked by hand:

      V*(0,1): "right" reaches the goal this step, Q(right) = 0 + 0.9*V(goal)
                = 0 + 0.9*0 = 0. Any other action bounces in place paying -1
                forever, which is worse. So V*(0,1) = 0, policy = right.
      V*(0,0): "right" reaches (0,1), Q(right) = -1 + 0.9*V*(0,1) = -1 + 0 = -1.
                Bouncing in place is again worse. So V*(0,0) = -1, policy = right.
    """
    mdp = GridWorld(rows=1, cols=3, terminals={(0, 2): 0.0}, step_reward=-1.0, noise=0.0)
    gamma = 0.9

    for solve in (value_iteration, policy_iteration):
        V, policy, _ = solve(mdp, gamma)
        assert V[(0, 0)] == pytest.approx(-1.0, abs=1e-4)
        assert V[(0, 1)] == pytest.approx(0.0, abs=1e-4)
        assert policy[(0, 0)] == "right"
        assert policy[(0, 1)] == "right"


@pytest.mark.parametrize(
    "rows,cols,noise,step_reward",
    [
        (4, 4, 0.0, -0.04),
        (4, 4, 0.2, -0.04),
        (6, 5, 0.2, -1.0),
        (8, 8, 0.1, -0.04),
    ],
)
def test_value_and_policy_iteration_agree(rows: int, cols: int, noise: float, step_reward: float) -> None:
    """Both algorithms solve the same Bellman optimality equation, so for
    the same MDP they must converge to the same optimal value function
    (and, except for rare tied-action states, the same greedy policy)."""
    goal = (rows - 1, cols - 1)
    mdp = GridWorld(
        rows=rows, cols=cols, terminals={goal: 1.0}, step_reward=step_reward, noise=noise
    )
    gamma = 0.95

    V_vi, policy_vi, _ = value_iteration(mdp, gamma)
    V_pi, policy_pi, _ = policy_iteration(mdp, gamma)

    for s in mdp.states():
        assert V_vi[s] == pytest.approx(V_pi[s], abs=1e-3)

    # Policies may differ only where two actions are genuinely tied in value;
    # check that every disagreement is in fact a tie, rather than requiring
    # literal policy equality.
    for s in mdp.states():
        if mdp.is_terminal(s):
            continue
        if policy_vi[s] != policy_pi[s]:
            from deep_dive.dp import q_value

            q_vi = q_value(mdp, s, policy_vi[s], gamma, V_vi)
            q_pi = q_value(mdp, s, policy_pi[s], gamma, V_vi)
            assert q_vi == pytest.approx(q_pi, abs=1e-3)


def test_optimal_policy_routes_around_a_pit() -> None:
    """3x3 grid, goal at (2,2), a pit at (1,1) with a large negative reward
    directly on the shortest diagonal-ish path. The optimal policy from
    (0,1) and (1,0), both adjacent to the pit, should not step into it
    when a same-length route around it exists."""
    mdp = GridWorld(
        rows=3,
        cols=3,
        terminals={(2, 2): 1.0, (1, 1): -10.0},
        step_reward=-0.04,
        noise=0.0,
    )
    gamma = 0.95
    _, policy, _ = value_iteration(mdp, gamma)

    assert policy[(0, 1)] != "down"  # would step into the pit at (1,1)
    assert policy[(1, 0)] != "right"  # would step into the pit at (1,1)


def test_policy_iteration_needs_no_more_outer_iterations_than_states() -> None:
    """Sanity bound: policy iteration strictly improves the policy (or
    stops) each outer loop, and there are only finitely many deterministic
    policies, so it must terminate, well within one iteration per
    non-terminal state for a small grid."""
    mdp = GridWorld(rows=5, cols=5, terminals={(4, 4): 1.0}, noise=0.1)
    _, _, iterations = policy_iteration(mdp, gamma=0.9)
    non_terminal_states = len(mdp.states()) - len(mdp.terminals)
    assert iterations <= non_terminal_states
