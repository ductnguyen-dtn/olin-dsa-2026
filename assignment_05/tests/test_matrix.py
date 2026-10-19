from divide_and_conquer.matrix import Matrix


def test_default_construction_is_zeros() -> None:
    m = Matrix(3)
    assert all(m.get(i, j) == 0.0 for i in range(3) for j in range(3))


def test_rejects_non_square_data() -> None:
    try:
        Matrix(2, [[1, 2, 3], [4, 5, 6]])
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for non-square data")


def test_get_set() -> None:
    m = Matrix(2)
    m.set(0, 1, 5.0)
    assert m.get(0, 1) == 5.0
    assert m.get(1, 0) == 0.0


def test_split_and_combine_round_trip() -> None:
    data = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]
    m = Matrix(4, data)
    top_left, top_right, bottom_left, bottom_right = m.split()
    assert top_left.n == 2
    assert top_left.get(0, 0) == 1 and top_left.get(1, 1) == 6
    assert top_right.get(0, 0) == 3 and top_right.get(1, 1) == 8
    assert bottom_left.get(0, 0) == 9 and bottom_left.get(1, 1) == 14
    assert bottom_right.get(0, 0) == 11 and bottom_right.get(1, 1) == 16

    combined = Matrix.combine(top_left, top_right, bottom_left, bottom_right)
    assert combined == m


def test_split_requires_even_size() -> None:
    m = Matrix(3)
    try:
        m.split()
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for odd-sized split")


def test_add_and_sub() -> None:
    a = Matrix(2, [[1, 2], [3, 4]])
    b = Matrix(2, [[10, 20], [30, 40]])
    assert (a + b) == Matrix(2, [[11, 22], [33, 44]])
    assert (b - a) == Matrix(2, [[9, 18], [27, 36]])


def test_equality() -> None:
    a = Matrix(2, [[1, 2], [3, 4]])
    b = Matrix(2, [[1, 2], [3, 4]])
    c = Matrix(2, [[1, 2], [3, 5]])
    assert a == b
    assert a != c
    assert a != "not a matrix"


def test_repr_contains_data() -> None:
    m = Matrix(1, [[7]])
    assert "7" in repr(m)
