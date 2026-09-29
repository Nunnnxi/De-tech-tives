# Operation: Evidence Lockers
# Cleans up 60 messy lines of case data, removes duplicates, and reports on ages and beats.

FILENAME = "wk04_data_raw_cases_dupes.txt"   # the messy file we're cleaning up

# --- STEP 1: READ + NORMALIZE ---
# "Normalize" just means making messy text consistent so we can compare it fairly
# (so "carter | m" and "CARTER | M" are recognized as the same record).
with open(FILENAME, encoding="utf-8") as f:       # open the file
    raw_lines = f.readlines()                     # read every line into a list of strings

normalized = []                                   # empty list ("locker") to hold cleaned-up lines

for line in raw_lines:                            # look at each raw line, one at a time
    line = line.strip()                           # remove leading/trailing spaces and the newline
    if line == "":                                # skip blank lines...
        continue                                  # ...they don't count as real records

    clean = line.upper()                          # force everything to UPPERCASE so casing doesn't matter
    normalized.append(clean)                      # add the cleaned line to our list

print(f"Lines in file:      {len(normalized)}")   # should print 60

# --- STEP 2: DEDUPE (only AFTER normalizing — order matters here) ---
# A set can only hold each value ONCE, so dumping a list into a set auto-removes exact duplicates.
unique_set = set(normalized)                      # {} of unique lines — duplicates silently vanish
unique_records = list(unique_set)                 # turn it back into a list so we can loop over it in order

duplicates_removed = len(normalized) - len(unique_records)   # how many lines were duplicates

print(f"Unique records:     {len(unique_records)}")
print(f"Duplicates removed: {duplicates_removed}")

# --- STEP 3: COLLECT AGES + COUNT OPEN CASES PER BEAT (dedupe FIRST, then analyze) ---
ages = []                        # empty list to hold every victim's age
per_beat = {}                    # empty dict ("labeled lockers"): beat name -> count of open cases

for rec in unique_records:                        # loop over the DEDUPED records only, not the raw ones
    fields = rec.split("|")                       # split the line into its 7 pieces using "|" as the divider

    age = int(fields[2].strip())                  # field 3 is age; strip spaces, convert text to a number
    ages.append(age)                              # add this age to our running list

    beat = fields[5].strip()                      # field 6 is the beat (patrol area)
    status = fields[6].strip()                    # field 7 is OPEN or CLOSED

    if status == "OPEN":                          # we only rank OPEN cases, so skip CLOSED ones
        per_beat[beat] = per_beat.get(beat, 0) + 1   # .get(beat, 0) means "0 if we haven't seen this beat yet"

# --- STEP 4: REPORT, outside the loop so it runs once after every record is processed ---
youngest = min(ages)                 # smallest number in the ages list
oldest = max(ages)                   # largest number in the ages list
average = sum(ages) / len(ages)      # add every age together, divide by how many ages there are

print()
print("---- AGE PROFILE (unique records only) ----")
print(f"Youngest: {youngest}")
print(f"Oldest:   {oldest}")
print(f"Average:  {average:.1f}")    # :.1f means "round to 1 decimal place"

print()
print("---- BEAT RANKING (most open cases first) ----")
# sorted(per_beat) alone would sort by the KEYS (beat names).
# key=lambda b: per_beat[b] tells it to sort by the VALUES (the counts) instead.
# reverse=True flips it so the biggest count comes first.
for beat in sorted(per_beat, key=lambda b: per_beat[b], reverse=True):
    count = per_beat[beat]           # look up how many open cases this beat has
    bar = "#" * count                # repeat "#" that many times to make a mini bar chart
    print(f"{beat:<10}{count:>3}  {bar}")   # beat left-aligned, count right-aligned, then the bar
