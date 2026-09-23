# ITSS/OPRE 3312 - Lecture 3: The First Filter
# Squad Lab: Operation First Filter
#
# Sweep every record in the case file, flag OPEN cases that have been
# unsolved 5+ years, and find the oldest OPEN case. The loop must not
# crash on blank or bad lines.

CURRENT_YEAR = 2026
STALE_YEARS = 5

DATA_FILE = "data/wk03_data_raw_cases_50.txt"

total_count = 0
open_count = 0
stale_count = 0
juvenile_open = 0
oldest_year = CURRENT_YEAR
oldest_name = ""

records = open(DATA_FILE)

for raw_line in records:
    line = raw_line.strip()

    # skip blank lines
    if line == "":
        continue

    fields = line.split("|")

    # skip bad/incomplete records
    if len(fields) != 7:
        continue

    name = fields[0].strip().title()
    age = int(fields[2].strip())
    date = fields[3].strip()
    year = int(date[0:4])
    status = fields[6].strip().upper()

    years_unsolved = CURRENT_YEAR - year
    total_count = total_count + 1

    if status == "OPEN":
        open_count = open_count + 1

        if age < 18:
            juvenile_open = juvenile_open + 1

        if year < oldest_year:
            oldest_year = year
            oldest_name = name

        if years_unsolved >= STALE_YEARS:
            stale_count = stale_count + 1
            print(name, ":", years_unsolved, "years", "*** STALE ***")
        else:
            print(name, ":", years_unsolved, "years")
    else:
        print(name, ":", years_unsolved, "years")

records.close()

print()
print("Total records:       ", total_count)
print("Open cases:          ", open_count)
print("Stale (>= 5 yrs):    ", stale_count)
print("Juveniles (open):    ", juvenile_open)
print("Oldest open case:    ", oldest_name, "(" + str(oldest_year) + ")")
