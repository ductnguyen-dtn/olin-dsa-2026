import random

import pytest

from divide_and_conquer.matrix import Matrix


def _random_matrix(n: int, rng: random.Random) -> Matrix:
    return Matrix(n, [[rng.uniform(-10, 10) for _ in range(n)] for _ in range(n)])


def _assert_close(a: Matrix, b: Matrix, tol: float = 1e-6) -> None:
    assert a.n == b.n
    for i in range(a.n):
        for j in range(a.n):
            assert abs(a.get(i, j) - b.get(i, j)) < tol, f"mismatch at ({i}, {j})"


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 7, 8, 16])
def test_strassen_matches_conventional_pure(n: int) -> None:
    """threshold=1 is pure Strassen, recursing to 1x1 scalar products. This
    also exercises the zero-padding path for every n that is not already a
    power of 2 (1, 3, 5, 7)."""
    rng = random.Random(n)
    a = _random_matrix(n, rng)
    b = _random_matrix(n, rng)
    conventional = a.multiply(b)
    strassen = a.strassen_multiply(b, threshold=1)
    assert conventional is not None
    assert strassen is not None
    _assert_close(conventional, strassen)


@pytest.mark.parametrize("threshold", [1, 2, 4, 8, 16])
def test_strassen_matches_conventional_at_various_thresholds(threshold: int) -> None:
    """Raising the threshold changes how much of the recursion gets
    offloaded to conventional multiplication (the hybrid approach), but the
    result must always be the same product."""
    rng = random.Random(42)
    n = 16
    a = _random_matrix(n, rng)
    b = _random_matrix(n, rng)
    conventional = a.multiply(b)
    strassen = a.strassen_multiply(b, threshold=threshold)
    assert conventional is not None
    assert strassen is not None
    _assert_close(conventional, strassen)


def test_strassen_incompatible_sizes_returns_none() -> None:
    a = Matrix(2)
    b = Matrix(3)
    assert a.strassen_multiply(b) is None


def test_strassen_identity() -> None:
    identity = Matrix(4, [[1 if i == j else 0 for j in range(4)] for i in range(4)])
    rng = random.Random(0)
    a = _random_matrix(4, rng)
    result = a.strassen_multiply(identity)
    assert result is not None
    _assert_close(result, a)
