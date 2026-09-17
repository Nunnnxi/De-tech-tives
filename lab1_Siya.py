record_1="CARTER, DEMARCUS | m | 36 | 2018-03-22 | 412 larkmoor lane | beat 352 | OPEN"
fields_1=record_1.strip().split(" | ")
name_1=fields_1[0].title()
sex_1=fields_1[1].upper()
age_1=int(fields_1[2])
date_1=fields_1[3]
year_1=int(date_1.split("-")[0])
addr_1=fields_1[4].title()
status_1=fields_1[6].upper()
years_unsolved=2026-year_1
summary=f"Name: {name_1}\nSex: {sex_1}\nAge: {age_1}\nDate: {date_1}\nAddress: {addr_1}\nStatus: {status_1}\nYears Unsolved: {years_unsolved}"
print(summary)
