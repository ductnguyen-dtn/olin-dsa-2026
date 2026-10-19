"""Run Smith-Waterman on the assignment's genome data and print the result.

Run with (from the assignment_05 directory, with the venv active)::

    PYTHONPATH=src python -m divide_and_conquer.run_alignment

Per the assignment instructions for Smith-Waterman, this aligns
``testAgainst`` against ``targetGenome``. As a correctness check, it also
confirms the local alignment's position in targetGenome overlaps the known
location of genomeSnippet within targetGenome (targetGenome is constructed
to fully contain genomeSnippet) -- if testAgainst is genuinely similar to
genomeSnippet, Smith-Waterman should find its best local match right where
genomeSnippet sits, without being told that location in advance.
"""

from __future__ import annotations

from divide_and_conquer.genome_data import GENOME_SNIPPET, TARGET_GENOME, TEST_AGAINST
from divide_and_conquer.sequence_alignment import smith_waterman


def main() -> None:
    result = smith_waterman(TEST_AGAINST, TARGET_GENOME)

    snippet_start = TARGET_GENOME.index(GENOME_SNIPPET)
    snippet_end = snippet_start + len(GENOME_SNIPPET)

    print(f"testAgainst length: {len(TEST_AGAINST)}")
    print(f"targetGenome length: {len(TARGET_GENOME)}")
    print(f"known genomeSnippet location in targetGenome: [{snippet_start}, {snippet_end})")
    print()
    print(f"Smith-Waterman score: {result.score}")
    print(f"alignment length: {len(result.aligned_a)}")
    print(f"testAgainst region matched: [{result.start_a}, {result.end_a})")
    print(f"targetGenome region matched: [{result.start_b}, {result.end_b})")
    print()
    print("aligned testAgainst: ", result.aligned_a)
    print("aligned targetGenome:", result.aligned_b)

    overlap_start = max(result.start_b, snippet_start)
    overlap_end = min(result.end_b, snippet_end)
    overlap = max(0, overlap_end - overlap_start)
    print()
    print(f"overlap with known genomeSnippet location: {overlap} bases")
    if overlap > 0:
        print("Smith-Waterman's best local match overlaps the known genomeSnippet region.")
    else:
        print("No overlap with the known genomeSnippet region -- unexpected, worth investigating.")


if __name__ == "__main__":
    main()
