CURRENT_YEAR = 2026
STALE_YEARS  = 5

DATA_FILE = "data/wk03_data_raw_cases_50.txt"

total_count    = 0
open_count     = 0
stale_count    = 0
juvenile_open  = 0
oldest_year    = CURRENT_YEAR
oldest_name    = ""

with open(DATA_FILE) as records:
    for raw_line in records:
        line = raw_line.strip()
        if line == "":
            continue

        fields = line.split("|")
        if len(fields) != 7:
            continue

        name   = fields[0].strip().title()
        age    = int(fields[2].strip())
        date   = fields[3].strip()
        year   = int(date[0:4])
        status = fields[6].strip().upper()

        years_unsolved = CURRENT_YEAR - year
        flag = "*** STALE ***" if status == "OPEN" and years_unsolved >= STALE_YEARS else ""

        print(f"{name}: {years_unsolved} years  {flag}".rstrip())

        total_count += 1
        if status == "OPEN":
            open_count += 1
            if age < 18:
                juvenile_open += 1
            if years_unsolved >= STALE_YEARS:
                stale_count += 1
            if year < oldest_year:
                oldest_year = year
                oldest_name = name

print()
print(f"Total records:        {total_count}")
print(f"Open cases:           {open_count}")
print(f"Stale (>= {STALE_YEARS} yrs):     {stale_count}")
print(f"Juveniles (open):     {juvenile_open}")
print(f"Oldest open case:     {oldest_name} ({oldest_year})")
