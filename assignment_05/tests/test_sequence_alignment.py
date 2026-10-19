from divide_and_conquer.sequence_alignment import smith_waterman


def test_wikipedia_worked_example() -> None:
    """From the Smith-Waterman Wikipedia page's worked example: sequences
    TGTTACGG and GGTTGACTA, scored match=+3/mismatch=-3/gap=-2, produce the
    alignment GTT-AC / GTTGAC with score 13 (5 matches at +3 = 15, minus one
    gap at -2 = 13)."""
    result = smith_waterman("TGTTACGG", "GGTTGACTA", match=3, mismatch=-3, gap=-2)
    assert result.score == 13
    assert result.aligned_a == "GTT-AC"
    assert result.aligned_b == "GTTGAC"


def test_identical_sequences_align_fully() -> None:
    result = smith_waterman("ACGTACGT", "ACGTACGT")
    assert result.aligned_a == "ACGTACGT"
    assert result.aligned_b == "ACGTACGT"
    assert result.start_a == 0 and result.end_a == 8
    assert result.start_b == 0 and result.end_b == 8


def test_no_similarity_gives_zero_score() -> None:
    # Every position mismatches and mismatch/gap penalties dominate, so the
    # best "alignment" is the empty one (score 0), per Smith-Waterman's
    # local-alignment floor of 0.
    result = smith_waterman("AAAA", "TTTT", match=1, mismatch=-10, gap=-10)
    assert result.score == 0
    assert result.aligned_a == ""
    assert result.aligned_b == ""


def test_finds_substring_match_within_longer_sequence() -> None:
    needle = "GATTACA"
    haystack = "XXXXXXGATTACAYYYYYY"
    result = smith_waterman(needle, haystack)
    assert result.aligned_a == needle
    assert result.aligned_b == needle
    assert haystack[result.start_b:result.end_b] == needle


def test_single_character_sequences() -> None:
    result = smith_waterman("A", "A")
    assert result.score > 0
    assert result.aligned_a == "A"
    assert result.aligned_b == "A"
