# intake_safe.py
# ITSS/OPRE 3312 - Lecture 6: "Bulletproof Intake"
# Squad Lab: Operation Bulletproof. Load 100 real-looking case rows from
# a CSV file. 11 of the rows are damaged on purpose. The goal is ZERO
# crashes: load what's loadable, and "quarantine" (set aside and log)
# anything broken instead of letting it kill the whole program.

# "csv" is Python's built-in module for reading comma-separated files.
# We need it instead of line.split(",") because some of our names have
# commas INSIDE them, like "KIRKLAND, MONICA, JR, III". The csv module
# knows that a comma inside quotes is part of the field, not a new field.
import csv


def parse_row(row):
    """Turn one CSV row (a list of 8 strings) into a clean case dict.

    Raises ValueError (with a reason) if the row is damaged in any way
    we recognize. We never silently "fix" bad data -- we either return
    a clean dict, or we raise, and let the caller decide what to do.

    SCOPE NOTE: "row" is a parameter. Every variable we make in this
    function (case_id, name, sex, age, ...) only exists while this
    function is running. The only way anything gets out is "return".
    """

    # Trap #1: a healthy row has exactly 8 fields (case_id, victim_name,
    # sex, age, date, address, beat, status). A truncated row is missing
    # some of the trailing fields, so len(row) will be smaller than 8.
    if len(row) != 8:
        raise ValueError(f"expected 8 fields, got {len(row)}")

    # Unpack the row into named pieces. This is just for readability --
    # row[0] and case_id now point at the same string.
    case_id = row[0].strip()
    name = row[1].strip().title()   # "carter, d" -> "Carter, D"
    sex = row[2].strip().upper()
    age_text = row[3].strip()
    date = row[4].strip()
    address = row[5].strip().title()
    beat = row[6].strip()
    status = row[7].strip().upper()

    # Trap #2: some ages were planted as the literal text "unknown"
    # instead of a number. int("unknown") raises ValueError on its own --
    # we don't need to catch and re-raise it, we just let Python's own
    # error bubble up out of this function. Whoever calls parse_row()
    # will see that same ValueError.
    age = int(age_text)

    # Trap #3: some rows have a blank date field (nothing between the
    # two commas). This one doesn't raise on its own, so we check for it
    # and raise it ourselves.
    if date == "":
        raise ValueError("missing date")

    # Every check above passed, so this row is clean. Hand back a dict
    # instead of a list, so the rest of the program can say case["age"]
    # instead of having to remember that age is row[3].
    return {
        "case_id": case_id,
        "name": name,
        "sex": sex,
        "age": age,
        "date": date,
        "address": address,
        "beat": beat,
        "status": status,
    }


def load_cases(path):
    """Read every row of the CSV at `path`, parse it, and sort the good
    rows from the bad ones.

    Returns (good, quarantine):
      good       -- a list of clean case dicts from parse_row()
      quarantine -- a list of (line_number, reason, raw_row_text) tuples,
                    one for every row that failed to parse
    """

    # Set up the two accumulators BEFORE the loop starts, same rule as
    # every earlier lab: set up before, update inside, report after.
    good = []
    quarantine = []

    # "with open(...) as f" opens the file AND guarantees it gets closed
    # again when we're done with it -- even if something inside the
    # "with" block crashes. That's safer than a plain open()/close() pair.
    # newline="" is required by the csv module so it handles line endings
    # correctly on every operating system.
    with open(path, newline="") as f:
        reader = csv.reader(f)

        # The first row of the file is the header (column names), not
        # data. next(reader) reads it and throws it away, so the loop
        # below only ever sees real case rows.
        next(reader)

        # enumerate(reader, start=2) numbers the rows starting at 2,
        # because the header was line 1. That way the line numbers we
        # print later match the line numbers you'd see in a text editor.
        for line_num, row in enumerate(reader, start=2):

            # Trap: one line in the file is completely blank. csv.reader
            # turns a blank line into an empty list, []. We skip it
            # entirely -- it isn't a case, so it's neither "loaded" nor
            # "quarantined", just ignored, the same way earlier labs
            # skipped blank lines with "continue".
            if row == []:
                continue

            # THE QUARANTINE PATTERN:
            # "try" means "attempt this, and if it raises an exception,
            # don't crash -- jump down to the matching except block."
            try:
                case = parse_row(row)
                good.append(case)

            # We catch ValueError SPECIFICALLY, not every possible error
            # (never use a bare "except:"). A bare except would also
            # swallow real bugs in our own code and hide them from us.
            except ValueError as err:
                # Rebuild a readable version of the original row so the
                # quarantine log shows what was actually in the file.
                raw_row_text = ",".join(row)
                quarantine.append((line_num, str(err), raw_row_text))

            # Notice there's no "else" or extra logic needed here -- the
            # loop just keeps going either way. One bad row never stops
            # us from reading the other 99.

    return good, quarantine


def report(good, quarantine):
    """Print the final intake report: counts, then the full quarantine log."""
    print(f"Rows loaded cleanly:   {len(good)}")
    print(f"Rows quarantined:      {len(quarantine)}")
    print()
    print("QUARANTINE LOG — every rejected row, with the reason:")
    for line_num, reason, raw_row_text in quarantine:
        print(f"  line {line_num:>3}: {reason:<45} | {raw_row_text}")


# ----- MAIN SCRIPT -----
# This only runs when you execute "python3 intake_safe.py" directly. It
# will NOT run when test_intake.py imports parse_row/load_cases from this
# file -- that's what the "if __name__" guard is for.
if __name__ == "__main__":
    good_cases, quarantine_log = load_cases("data/wk06_data_raw_cases_100.csv")
    report(good_cases, quarantine_log)
