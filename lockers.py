# lockers.py
# ITSS/OPRE 3312 - Lecture 4: "Evidence Lockers"
# Squad Lab: dedupe the case file, profile victim ages,
# and rank open cases by beat.

# Step 1: open the raw data file and normalize every line.
# Normalizing means stripping whitespace and forcing uppercase so that
# the same record typed two different ways still looks identical.
data_file = open("wk04_data_raw_cases_dupes.txt")

normalized_lines = []          # list: every normalized line, duplicates and all

for line in data_file:
    clean_line = line.strip().upper()

    # Skip blank lines instead of crashing on them.
    if clean_line == "":
        continue

    normalized_lines.append(clean_line)

data_file.close()

# Confirm we read all 60 lines from the file.
print(f"Lines in file:      {len(normalized_lines)}")

# Step 2: dedupe with a set. A set automatically drops duplicate entries.
unique_records = set(normalized_lines)

duplicates_removed = len(normalized_lines) - len(unique_records)
print(f"Unique records:     {len(unique_records)}")
print(f"Duplicates removed: {duplicates_removed}")

# Step 3: loop the UNIQUE records only. Collect ages into a list, and
# count OPEN cases per beat in a dictionary.
ages = []            # list: victim age from every unique record
per_beat = {}        # dict: beat -> how many OPEN cases in that beat

for record in unique_records:

    # Split the record into its 7 pipe-separated fields.
    fields = record.split("|")

    age = int(fields[2].strip())
    beat = fields[5].strip()
    status = fields[6].strip()

    ages.append(age)

    if status == "OPEN":
        # First time we see this beat, start it at 1. Otherwise, add 1.
        if beat in per_beat:
            per_beat[beat] += 1
        else:
            per_beat[beat] = 1

# Step 4: report the results AFTER the loop is done.
print()
print("----- AGE PROFILE -----")
print(f"Youngest: {min(ages)}")
print(f"Oldest:   {max(ages)}")
print(f"Average:  {round(sum(ages) / len(ages), 1)}")

print()
print("----- OPEN CASES BY BEAT (most burdened first) -----")

# sorted(per_beat, key=per_beat.get, reverse=True) sorts the beat names
# by their open-case count, biggest count first.
for beat in sorted(per_beat, key=per_beat.get, reverse=True):
    count = per_beat[beat]
    bar = "#" * count
    print(f"{beat:<10}{count:>3}  {bar}")
