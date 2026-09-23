#open and read the file, records make it into list
with open("data/wk03_data_raw_cases_50.txt", "r") as file:
    records = file.readlines()

total_count=0
open_count=0
stale_count=0
juvenile_count=0

oldest_year = 2026
oldest_name = ""

#run code for each record 
for line in records:
    #delete extra spaces at the beginning and end of the line
    line = line.strip()
#check blank lines and skip them
    if line == "":
        continue
#make a list of fields by splitting the line at the pipe character
    fields = line.split("|")

    name = fields[0].strip().title()
    #make string into integer
    age = int(fields[2].strip())
    year = int(fields[3].strip()[0:4])
    status = fields[6].strip().upper()

    years_unsolved = 2026 - year
#+1 every time a record is processed
    total_count = total_count + 1
#print case with name and years unsolved
    print(f"{name}: {years_unsolved} years unsolved")
#solve only open case
    if status == "OPEN":
        open_count = open_count + 1

        if age < 18:
            juvenile_count = juvenile_count + 1

        if years_unsolved >= 5:
            stale_count = stale_count + 1
            print("*** STALE ***")
#look for the oldest case
        if year < oldest_year:
            oldest_year = year
            oldest_name = name

print()
print(f"Total records: {total_count}")
print(f"Open cases: {open_count}")
print(f"Stale (>= 5 yrs): {stale_count}")
print(f"Juvenile open cases: {juvenile_count}")
print(f"Oldest open case: {oldest_name} ({oldest_year})")