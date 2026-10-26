import pytest

from deep_dive.gridworld import GridWorld


def test_states_excludes_walls() -> None:
    mdp = GridWorld(rows=2, cols=2, terminals={(1, 1): 1.0}, walls=frozenset({(0, 1)}))
    assert set(mdp.states()) == {(0, 0), (1, 0), (1, 1)}


def test_terminal_has_no_actions_or_transitions() -> None:
    mdp = GridWorld(rows=2, cols=2, terminals={(1, 1): 1.0})
    assert mdp.actions((1, 1)) == ()
    assert mdp.transitions((1, 1), "up") == []


def test_deterministic_move_into_wall_bounces_back() -> None:
    mdp = GridWorld(rows=1, cols=2, terminals={(0, 1): 1.0}, noise=0.0)
    # Only action out of (0, 0) that matters is "left", which runs off the grid.
    [(prob, next_s, reward)] = mdp.transitions((0, 0), "left")
    assert prob == 1.0
    assert next_s == (0, 0)
    assert reward == mdp.step_reward


def test_deterministic_transition_has_single_outcome() -> None:
    mdp = GridWorld(rows=1, cols=3, terminals={(0, 2): 1.0}, noise=0.0)
    outcomes = mdp.transitions((0, 1), "right")
    assert len(outcomes) == 1
    prob, next_s, reward = outcomes[0]
    assert prob == 1.0
    assert next_s == (0, 2)
    assert reward == 1.0  # terminal reward overrides step_reward on entry


def test_stochastic_transitions_sum_to_one() -> None:
    mdp = GridWorld(rows=4, cols=4, terminals={(3, 3): 1.0}, noise=0.2)
    for s in mdp.states():
        if mdp.is_terminal(s):
            continue
        for a in mdp.actions(s):
            total_prob = sum(p for p, _, _ in mdp.transitions(s, a))
            assert total_prob == pytest.approx(1.0)


def test_noise_splits_evenly_across_perpendiculars() -> None:
    mdp = GridWorld(rows=3, cols=3, terminals={(2, 2): 1.0}, noise=0.2)
    outcomes = mdp.transitions((1, 1), "right")
    # intended "right", perpendiculars are "up" and "down"
    probs = sorted(p for p, _, _ in outcomes)
    assert probs == pytest.approx([0.1, 0.1, 0.8])


def test_terminal_cannot_also_be_a_wall() -> None:
    with pytest.raises(ValueError):
        GridWorld(rows=2, cols=2, terminals={(0, 0): 1.0}, walls=frozenset({(0, 0)}))


def test_invalid_noise_rejected() -> None:
    with pytest.raises(ValueError):
        GridWorld(rows=2, cols=2, terminals={(1, 1): 1.0}, noise=1.5)
