record_4 = "Nguyen, Daniel | m | 17 | 2018-04-03 | 2846 QUAIL RIDGE ROAD | beat 537 | Open"
record_5 ="BOOKER, TERRENCE | M | 41 | 2018-11-08 | 907 n. calloway drive | Beat 442 | OPEN"
fields_4= record_4.strip().split(" | ")
name_4 =fields_4[0].title()
sex_4 = fields_4[1].upper()
age_4 = int(fields_4[2])
date_4 = fields_4[3]
year_4 = int(date_4[0:4])
address_4 = fields_4[4].title()
status_4 = fields_4[6]
year4_unsolved=2026-year_4
summary_4 = f"CASE: {name_4}  ({sex_4}, {age_4}) | {address_4} | {status_4} - {year4_unsolved} years without an arrest"
print(summary_4)

fields_5= record_5.strip().split(" | ")
name_5 =fields_5[0].title()
sex_5 = fields_5[1].upper()
age_5 = int(fields_5[2])
date_5 = fields_5[3]
year_5 = int(date_5[0:4])
address_5 = fields_5[4].title()
status_5 = fields_5[6]
year5_unsolved=2026-year_5
summary_5 = f"CASE: {name_5}  ({sex_5}, {age_5}) | {address_5} | {status_5} - {year5_unsolved} years without an arrest"
print(summary_5)

