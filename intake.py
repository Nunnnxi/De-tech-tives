with open("data/raw_cases.txt") as f:
    lines = f.readlines()

# Record 1 — do this one together
line = lines[0].strip()
fields = line.split("|")

name = fields[0].strip().title()
sex = fields[1].strip().upper()
age = int(fields[2].strip())
date_reported = fields[3].strip()
address = fields[4].strip().title()
beat = fields[5].strip().title()
status = fields[6].strip().upper()

year_reported = int(date_reported.split("-")[0])
years_unsolved = 2026 - year_reported

print(f"{name} | {sex} | {age} | {address} | {beat} | {status} | {years_unsolved} yrs unsolved")
