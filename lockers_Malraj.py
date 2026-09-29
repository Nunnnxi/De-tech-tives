# lockers.py - Week 4: Evidence Lockers
# Normalize -> dedupe -> collect -> count -> rank

# ---- Step 1: read the file ----
with open("wk04_data_raw_cases_dupes.txt") as f:
    raw_lines = f.readlines()

# ---- Step 2: normalize every line (strip + upper) into a list ----
normalized = []
for line in raw_lines:
    clean = line.strip().upper()
    if clean == "":          # skip blank lines so they don't inflate counts
        continue
    normalized.append(clean)

# ---- Step 3: dedupe with a set (AFTER normalizing) ----
unique = set(normalized)
duplicates = len(normalized) - len(unique)

# ---- Step 4: loop UNIQUE records -> ages list + open cases per beat dict ----
ages = []
per_beat = {}

for rec in unique:
    parts = rec.split("|")
    # fields: 0 name, 1 sex, 2 age, 3 date, 4 address, 5 beat, 6 status
    age = int(parts[2].strip())
    ages.append(age)

    beat = parts[5].strip().replace("BEAT", "").strip()   # "BEAT 352" -> "352"
    status = parts[6].strip()

    if status == "OPEN":
        if beat in per_beat:
            per_beat[beat] += 1
        else:
            per_beat[beat] = 1

# ---- Step 5: print the report ----
print("=== DEDUPE REPORT ===")
print(f"Lines in file:      {len(normalized)}")
print(f"Unique records:     {len(unique)}")
print(f"Duplicates removed: {duplicates}")

print("\n=== VICTIM AGE PROFILE ===")
average = sum(ages) / len(ages)
print(f"Youngest {min(ages)} / Oldest {max(ages)} / Average {average:.1f}")

print("\n=== OPEN CASES PER BEAT (most burdened first) ===")
for beat in sorted(per_beat, key=per_beat.get, reverse=True):
    count = per_beat[beat]
    bar = "#" * count
    print(f"Beat {beat:<6}{count:>3}  {bar}")
