# first_filter.py
# ITSS/OPRE 3312 - Lecture 3: "The First Filter"
# Squad Lab: loop through 50 case records, flag stale open cases,
# and print the final counts report.

# The "current" year, used to figure out how long a case has been unsolved.
CURRENT_YEAR = 2026

# Step 1: set up the accumulators BEFORE the loop starts (slide 7's rule:
# set up before, update inside, report after).
total_records = 0          # how many records we looked at
open_count = 0              # how many cases are still OPEN
stale_count = 0              # how many OPEN cases are 5+ years old
juvenile_open_count = 0      # how many OPEN cases have a victim under 18
oldest_year = CURRENT_YEAR    # start high, so the first OPEN case beats it
oldest_name = ""

# Step 2: open the data file and loop over it, one line (one record) at a time.
data_file = open("data/wk03_data_raw_cases_50.txt")

for line in data_file:

    # Strip whitespace/newline off the line first.
    line = line.strip()

    # Skip blank lines instead of crashing on them (slide 8's continue).
    if line == "":
        continue

    # Split the record into its 7 pipe-separated fields.
    fields = line.split("|")

    # Pull out each field, cleaning it up the same way lab1 did.
    name = fields[0].strip().title()
    age = int(fields[2].strip())
    year = int(fields[3].strip().split("-")[0])
    status = fields[6].strip().upper()

    # How many years this case has been sitting unsolved.
    years_unsolved = CURRENT_YEAR - year

    # Count the record and print name + years_unsolved for every one.
    total_records = total_records + 1
    print(f"{name}: {years_unsolved} years unsolved")

    # Step 3: the flags only matter for cases that are still OPEN.
    if status == "OPEN":
        open_count = open_count + 1

        # Flag it once it's been open 5+ years.
        if years_unsolved >= 5:
            stale_count = stale_count + 1
            print("    *** STALE ***")

        # Count juvenile victims (age < 18) among the OPEN cases.
        if age < 18:
            juvenile_open_count = juvenile_open_count + 1

        # Step 4: keep track of the single oldest OPEN case.
        if year < oldest_year:
            oldest_year = year
            oldest_name = name

data_file.close()

# Step 5: report the totals AFTER the loop is done.
print()
print("----- CASE AUDIT REPORT -----")
print(f"Total records:        {total_records}")
print(f"Open cases:           {open_count}")
print(f"Stale (>= 5 yrs):     {stale_count}")
print(f"Juvenile open cases:  {juvenile_open_count}")
print(f"Oldest open case:     {oldest_name} ({oldest_year})")
