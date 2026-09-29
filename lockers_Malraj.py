# lockers_Malraj.py - Week 4: Evidence Lockers
# Author: Meghana Rao Malraj
# Goal: clean up the raw case file, remove duplicate records,
#       profile victim ages, and rank beats by number of open cases.
# Order of work: normalize -> dedupe -> collect -> count -> rank

# ---------------------------------------------------------------
# STEP 1: Read the file
# ---------------------------------------------------------------
# Open the raw data file and read every line into a list.
# "with" closes the file automatically when we're done.
with open("wk04_data_raw_cases_dupes.txt") as f:
    raw_lines = f.readlines()   # list of strings, one per line

# ---------------------------------------------------------------
# STEP 2: Normalize every line (LIST)
# ---------------------------------------------------------------
# The same record can appear with different spacing or capitals,
# e.g. "  Reyes, Lamar | m" vs "REYES, LAMAR | M".
# We make every line consistent BEFORE deduping, or the set
# would treat those as different records.
normalized = []                         # empty list to collect cleaned lines
for line in raw_lines:
    clean = line.strip().upper()        # remove outer spaces/newline, make uppercase
    if clean == "":                     # skip blank lines so they don't inflate counts
        continue
    normalized.append(clean)            # add the cleaned line to the end of the list

# ---------------------------------------------------------------
# STEP 3: Dedupe (SET)
# ---------------------------------------------------------------
# A set only keeps one copy of each item, so converting the list
# to a set removes the duplicate records automatically.
unique = set(normalized)
duplicates = len(normalized) - len(unique)   # how many copies were removed

# ---------------------------------------------------------------
# STEP 4: Collect ages and count open cases per beat (LIST + DICT)
# ---------------------------------------------------------------
ages = []        # list of every victim's age (for min / max / average)
per_beat = {}    # dictionary: beat number -> number of OPEN cases

# Loop over the UNIQUE records only, so duplicates don't skew stats
for rec in unique:
    # Split the record into fields wherever there is a "|"
    # Field order: 0 name, 1 sex, 2 age, 3 date, 4 address, 5 beat, 6 status
    parts = rec.split("|")

    # Age is stored as text, so convert it to a number before saving
    age = int(parts[2].strip())
    ages.append(age)

    # Beat looks like "BEAT 352" -> remove the word "BEAT" to keep just "352"
    beat = parts[5].strip().replace("BEAT", "").strip()
    status = parts[6].strip()

    # Counting pattern: only count cases that are still OPEN
    if status == "OPEN":
        if beat in per_beat:
            per_beat[beat] += 1     # seen this beat before: add one
        else:
            per_beat[beat] = 1      # first time seeing this beat: start at 1

# ---------------------------------------------------------------
# STEP 5: Print the report
# ---------------------------------------------------------------
# Part A: dedupe numbers
print("=== DEDUPE REPORT ===")
print(f"Lines in file:      {len(normalized)}")
print(f"Unique records:     {len(unique)}")
print(f"Duplicates removed: {duplicates}")

# Part B: victim age profile (built-in list functions do the math)
print("\n=== VICTIM AGE PROFILE ===")
average = sum(ages) / len(ages)
print(f"Youngest {min(ages)} / Oldest {max(ages)} / Average {average:.1f}")  # .1f = 1 decimal place

# Part C: rank beats from most open cases to fewest
# sorted(per_beat) sorts the keys; key=per_beat.get sorts them by their
# counts instead; reverse=True puts the biggest count first.
print("\n=== OPEN CASES PER BEAT (most burdened first) ===")
for beat in sorted(per_beat, key=per_beat.get, reverse=True):
    count = per_beat[beat]
    bar = "#" * count                               # simple text bar chart, e.g. 3 -> ###
    print(f"Beat {beat:<6}{count:>3}  {bar}")       # <6 and >3 line up the columns
