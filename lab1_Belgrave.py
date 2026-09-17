# Import datetime so we can get today's date/year
from datetime import datetime

# Raw case record as a single pipe-delimited string
record_3 = "OKAFOR, SAMUEL J | M | 55 | 2018-07-09 | 1519 westhollow avenue | beat 341 | OPEN"

# Grab the current year to later calculate how long the case has been unsolved
current_year = datetime.now().year

# strip everything
# Split the record on '|' into separate fields, trimming whitespace from each piece
fields = [f.strip() for f in record_3.split('|')]

# Field 0: person's name, formatted to title case (e.g. "Okafor, Samuel J")
name = fields[0].title()
# Field 1: sex, normalized to uppercase (e.g. "M")
sex = fields[1].upper()
# Field 2: age, converted from string to integer
age = int(fields[2])
# Field 3: date of the case as a string (e.g. "2018-07-09")
date = fields[3]
# Extract the year portion (first 4 characters) of the date and convert to int
year = int(date[0:4])
# Field 4: street address, formatted to title case
address = fields[4].title()
# Field 6: case status, normalized to uppercase (e.g. "OPEN")
status = fields[6].upper()

# compute everything
# Number of years the case has remained unsolved, based on current year vs. case year
years_unsolved = current_year - year

# report everything
# Build a formatted summary string combining all the parsed/computed fields
summary = f"CASE: {name} ({sex}, {age}) {date} | {address} | Status: {status} | YEARS UNSOLVED: {years_unsolved}"

# Output the final case summary to the console
print(summary)