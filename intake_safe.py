import csv
import os

# find the CSV in the same folder as this file, no matter where you run it from
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wk06_data_raw_cases_100.csv")


def parse_row(row):
    """Check one row and turn it into a dict, or raise ValueError with the reason."""
    if len(row) != 8:
        raise ValueError(f"expected 8 fields, got {len(row)}")
    age = int(row[3])
    if row[4].strip() == "":
        raise ValueError("missing date")
    return {
        "case_id": row[0].strip(),
        "name": row[1].strip().title(),
        "sex": row[2].strip().upper(),
        "age": age,
        "date": row[4].strip(),
        "address": row[5].strip(),
        "beat": row[6].strip(),
        "status": row[7].strip().upper(),
    }


def load_cases(path):
    """Read the CSV and return (good rows, quarantine log)."""
    good = []
    quarantine = []
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader)  # skip the header
        # start=2 because the header is line 1
        for line_num, row in enumerate(reader, start=2):
            if row == []:  # skip the blank line
                continue
            try:
                good.append(parse_row(row))
            except ValueError as err:
                quarantine.append((line_num, str(err), ",".join(row)))
    return good, quarantine


def report(good, quarantine):
    """Print how many rows loaded, how many were quarantined, and why."""
    print("Rows loaded cleanly:", len(good))
    print("Rows quarantined:   ", len(quarantine))
    print()
    print("QUARANTINE LOG - every rejected row, with the reason:")
    for line_num, reason, text in quarantine:
        print(f"  line {line_num:>3}: {reason:<55} | {text}")


# only runs when you run this file, not when the test file imports it
if __name__ == "__main__":
    good, quarantine = load_cases(DATA_FILE)
    report(good, quarantine)
