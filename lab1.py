# Record 2
record2 = "reyes, miguel|M|32|2018-05-17| 3308 DELAFORD STREET |Beat 347|open"

fields2 = record2.strip().split("|")
name   = fields2[0].title()
sex    = fields2[1].upper()
age    = int(fields2[2])
date   = fields2[3]
year   = int(date[0:4])
addr   = fields2[4].strip().title()
status = fields2[6].upper()

summary2 = f"{name}, {sex}, age {age}, {addr}, {status}, filed {year}"
print(summary2)
