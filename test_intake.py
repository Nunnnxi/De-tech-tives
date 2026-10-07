# test_intake.py
# ITSS/OPRE 3312 - Lecture 6: "Bulletproof Intake"
# Proof, not vibes: these tests PROVE parse_row() behaves correctly,
# instead of us just eyeballing the printed report and hoping.
#
# Run with:  pytest test_intake.py
# Green dots (or "3 passed") means every test below succeeded.

import pytest

# Import the function we're testing from our own file.
from intake_safe import parse_row


def test_good_row_parses():
    """A clean, well-formed row should parse with no error."""
    row = [
        "CC-1", " carter, d ", "m", "36",
        "2018-03-22", "412 larkmoor", "352", "open",
    ]

    case = parse_row(row)

    # "assert" means "this must be true, or the test fails."
    # age should have been converted from the string "36" to the int 36.
    assert case["age"] == 36
    # name should have been stripped and title-cased.
    assert case["name"] == "Carter, D"


def test_bad_age_rejected():
    """A row with a non-numeric age ('unknown') must raise ValueError."""
    row = [
        "CC-2", "carter, d", "m", "unknown",
        "2018-03-22", "412 larkmoor", "352", "open",
    ]

    # "with pytest.raises(ValueError):" means: the test only PASSES if
    # the code inside this block actually raises a ValueError. If
    # parse_row() returned normally instead of raising, this test fails.
    with pytest.raises(ValueError):
        parse_row(row)


def test_truncated_row_rejected():
    """A row that's missing trailing fields must raise ValueError."""
    # This row only has 6 fields instead of the required 8 (no beat or
    # status), the same kind of damage planted in the real CSV.
    row = ["CC-3", "carter, d", "m", "36", "2018-03-22", "412 larkmoor"]

    with pytest.raises(ValueError):
        parse_row(row)
