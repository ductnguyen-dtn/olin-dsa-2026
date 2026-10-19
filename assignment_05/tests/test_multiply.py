from divide_and_conquer.matrix import Matrix


def test_multiply_2x2_hand_computed() -> None:
    a = Matrix(2, [[1, 2], [3, 4]])
    b = Matrix(2, [[5, 6], [7, 8]])
    # [[1*5+2*7, 1*6+2*8], [3*5+4*7, 3*6+4*8]] = [[19, 22], [43, 50]]
    expected = Matrix(2, [[19, 22], [43, 50]])
    assert a.multiply(b) == expected


def test_multiply_identity() -> None:
    identity = Matrix(3, [[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    a = Matrix(3, [[2, 3, 4], [5, 6, 7], [8, 9, 10]])
    assert a.multiply(identity) == a
    assert identity.multiply(a) == a


def test_multiply_incompatible_sizes_returns_none() -> None:
    a = Matrix(2)
    b = Matrix(3)
    assert a.multiply(b) is None


def test_mul_operator_matches_multiply() -> None:
    a = Matrix(2, [[1, 2], [3, 4]])
    b = Matrix(2, [[5, 6], [7, 8]])
    assert (a * b) == a.multiply(b)


def test_mul_operator_raises_on_mismatch() -> None:
    a = Matrix(2)
    b = Matrix(3)
    try:
        a * b
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for mismatched * operands")


def test_multiply_non_commutative_in_general() -> None:
    a = Matrix(2, [[1, 2], [0, 1]])
    b = Matrix(2, [[1, 0], [3, 1]])
    assert a.multiply(b) != b.multiply(a)
