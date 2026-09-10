from datetime import datetime
record_3 = "OKAFOR, SAMUEL J | M | 55 | 2018-07-09 | 1519 westhollow avenue | beat 341 | OPEN"
current_year = datetime.now().year
# strip everything
fields = [f.strip() for f in record_3.split('|')]

name = fields[0].title()
sex = fields[1].upper()
age = int(fields[2])
date = fields[3]
year = int(date[0:4])
address = fields[4].title()
status = fields[6].upper()

# compute everything
years_unsolved = current_year - year

# report everything
summary = f"CASE: {name} ({sex}, {age}) {date} | {address} | Status: {status} | YEARS UNSOLVED: {years_unsolved}"

print(summary)