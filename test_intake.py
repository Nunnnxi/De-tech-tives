import pytest
from intake_safe import parse_row


def test_good_row_parses():
    """A clean row turns into a dict with the right values."""
    row = ["CC-1", " carter, d ", "m", "36", "2018-03-22", "412 larkmoor", "352", "open"]
    case = parse_row(row)
    assert case["age"] == 36
    assert case["name"] == "Carter, D"


def test_bad_age_rejected():
    """An age of 'unknown' raises ValueError."""
    row = ["CC-1", " carter, d ", "m", "unknown", "2018-03-22", "412 larkmoor", "352", "open"]
    with pytest.raises(ValueError):
        parse_row(row)


def test_missing_date_rejected():
    """An empty date raises ValueError."""
    row = ["CC-1", " carter, d ", "m", "36", "", "412 larkmoor", "352", "open"]
    with pytest.raises(ValueError):
        parse_row(row)


# lets you run the tests with the Run button too
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
