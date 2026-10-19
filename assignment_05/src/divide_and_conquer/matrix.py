"""A square matrix type with conventional and Strassen multiplication.

Strassen's algorithm multiplies two n x n matrices using 7 recursive
multiplications of (n/2) x (n/2) submatrices instead of the 8 a direct
block-multiplication would need, trading one multiplication for several
extra additions. Since addition is cheaper than multiplication, this lowers
the recurrence from T(n) = 8T(n/2) + Theta(n^2) (which solves to Theta(n^3),
the same as conventional multiplication) to T(n) = 7T(n/2) + Theta(n^2),
which by the master theorem solves to Theta(n^log2(7)) = Theta(n^2.807...).

See docs/strassen_analysis.md for the full derivation and benchmark results.
"""

from __future__ import annotations

from collections.abc import Sequence


class Matrix:
    """A square matrix of floats, stored as a list of row lists."""

    def __init__(self, n: int, data: Sequence[Sequence[float]] | None = None) -> None:
        if n < 1:
            raise ValueError("matrix size must be at least 1")
        if data is None:
            self._data: list[list[float]] = [[0.0] * n for _ in range(n)]
        else:
            if len(data) != n or any(len(row) != n for row in data):
                raise ValueError("data must be an n x n grid")
            self._data = [[float(value) for value in row] for row in data]
        self.n = n

    def get(self, row: int, col: int) -> float:
        return self._data[row][col]

    def set(self, row: int, col: int, value: float) -> None:
        self._data[row][col] = value

    def split(self) -> tuple[Matrix, Matrix, Matrix, Matrix]:
        """Split this even-sized matrix into four n/2 x n/2 quadrants:
        (top_left, top_right, bottom_left, bottom_right)."""
        if self.n % 2 != 0:
            raise ValueError("split requires an even-sized matrix")
        half = self.n // 2
        top_left = [row[:half] for row in self._data[:half]]
        top_right = [row[half:] for row in self._data[:half]]
        bottom_left = [row[:half] for row in self._data[half:]]
        bottom_right = [row[half:] for row in self._data[half:]]
        return (
            Matrix(half, top_left),
            Matrix(half, top_right),
            Matrix(half, bottom_left),
            Matrix(half, bottom_right),
        )

    @staticmethod
    def combine(top_left: Matrix, top_right: Matrix, bottom_left: Matrix, bottom_right: Matrix) -> Matrix:
        """Inverse of split(): join four equally-sized quadrants into one
        matrix twice their size."""
        half = top_left.n
        n = half * 2
        data = [[0.0] * n for _ in range(n)]
        for i in range(half):
            for j in range(half):
                data[i][j] = top_left.get(i, j)
                data[i][j + half] = top_right.get(i, j)
                data[i + half][j] = bottom_left.get(i, j)
                data[i + half][j + half] = bottom_right.get(i, j)
        return Matrix(n, data)

    def __add__(self, other: Matrix) -> Matrix:
        self._check_same_size(other)
        n = self.n
        data = [[self._data[i][j] + other._data[i][j] for j in range(n)] for i in range(n)]
        return Matrix(n, data)

    def __sub__(self, other: Matrix) -> Matrix:
        self._check_same_size(other)
        n = self.n
        data = [[self._data[i][j] - other._data[i][j] for j in range(n)] for i in range(n)]
        return Matrix(n, data)

    def __mul__(self, other: Matrix) -> Matrix:
        """``A * B`` via conventional multiplication. Raises ValueError on a
        dimension mismatch, since operator overloading has no sensible way
        to return None here; use multiply() directly if you want the
        Optional-returning behavior the assignment describes."""
        result = self.multiply(other)
        if result is None:
            raise ValueError(f"size mismatch: {self.n} vs {other.n}")
        return result

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Matrix):
            return NotImplemented
        return self.n == other.n and self._data == other._data

    def __repr__(self) -> str:
        rows = ", ".join(str(row) for row in self._data)
        return f"Matrix({self.n}, [{rows}])"

    def _check_same_size(self, other: Matrix) -> None:
        if self.n != other.n:
            raise ValueError(f"size mismatch: {self.n} vs {other.n}")

    def multiply(self, other: Matrix) -> Matrix | None:
        """Conventional matrix multiplication, Theta(n^3).

        Returns this * other if the dimensions are compatible (same n,
        since both matrices are square) and None otherwise.
        """
        if self.n != other.n:
            return None
        n = self.n
        result = [[0.0] * n for _ in range(n)]
        for i in range(n):
            row_i = self._data[i]
            result_i = result[i]
            for k in range(n):
                a_ik = row_i[k]
                if a_ik == 0.0:
                    continue
                other_k = other._data[k]
                for j in range(n):
                    result_i[j] += a_ik * other_k[j]
        return Matrix(n, result)

    def strassen_multiply(self, other: Matrix, threshold: int = 1) -> Matrix | None:
        """Strassen's divide-and-conquer multiplication.

        Returns this * other if the dimensions are compatible and None
        otherwise, matching multiply()'s contract.

        Non-power-of-2 sizes are handled by padding both matrices with
        zero rows/columns up to the next power of 2, running Strassen on
        the padded matrices, then cropping the product back down -- padding
        with zeros doesn't change the product's top-left n x n block, since
        the extra rows/columns only ever multiply against zeros.

        threshold is the submatrix size at or below which this falls back
        to conventional multiplication instead of recursing further.
        threshold=1 (the default) is "pure" Strassen, recursing all the way
        to 1x1 scalar products. Raising it implements the hybrid approach
        the assignment asks about: see docs/strassen_analysis.md for why
        pure Strassen is not actually the fastest choice in practice.
        """
        if self.n != other.n:
            return None
        padded_n = _next_power_of_two(self.n)
        padded_self = self._padded_to(padded_n)
        padded_other = other._padded_to(padded_n)
        product = _strassen(padded_self, padded_other, threshold)
        return product._cropped_to(self.n)

    def _padded_to(self, size: int) -> Matrix:
        if size == self.n:
            return self
        data = [[0.0] * size for _ in range(size)]
        for i in range(self.n):
            row = data[i]
            src_row = self._data[i]
            for j in range(self.n):
                row[j] = src_row[j]
        return Matrix(size, data)

    def _cropped_to(self, size: int) -> Matrix:
        if size == self.n:
            return self
        data = [row[:size] for row in self._data[:size]]
        return Matrix(size, data)


def _next_power_of_two(n: int) -> int:
    power = 1
    while power < n:
        power *= 2
    return power


def _strassen(a: Matrix, b: Matrix, threshold: int) -> Matrix:
    """Multiply two same-size, power-of-2-sized matrices via Strassen's
    algorithm. Formulas follow the Wikipedia description of the algorithm
    (see module docstring and docs/strassen_analysis.md for the warning
    about incorrect writeups elsewhere)."""
    n = a.n
    if n <= threshold:
        result = a.multiply(b)
        assert result is not None  # same size by construction
        return result

    a11, a12, a21, a22 = a.split()
    b11, b12, b21, b22 = b.split()

    m1 = _strassen(a11 + a22, b11 + b22, threshold)
    m2 = _strassen(a21 + a22, b11, threshold)
    m3 = _strassen(a11, b12 - b22, threshold)
    m4 = _strassen(a22, b21 - b11, threshold)
    m5 = _strassen(a11 + a12, b22, threshold)
    m6 = _strassen(a21 - a11, b11 + b12, threshold)
    m7 = _strassen(a12 - a22, b21 + b22, threshold)

    c11 = m1 + m4 - m5 + m7
    c12 = m3 + m5
    c21 = m2 + m4
    c22 = m1 - m2 + m3 + m6

    return Matrix.combine(c11, c12, c21, c22)
