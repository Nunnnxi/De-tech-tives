total = open_count = stale_count = juveniles = 0
oldest_name, oldest_year = "", None

with open("data/wk03_data_raw_cases_50.txt") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 7:
            continue
        name = parts[0]
        age = int(parts[2])
        year = int(parts[3][:4])
        status = parts[6].upper()
        years_unsolved = 2026 - year

        total += 1
        flag = ""
        if status == "OPEN":
            open_count += 1
            if years_unsolved >= 5:
                flag = "*** STALE ***"
                stale_count += 1
            if age < 18:
                juveniles += 1
            if oldest_year is None or year < oldest_year:
                oldest_name, oldest_year = name, year
        print(name, years_unsolved, flag)

print("Total:", total)
print("Open:", open_count)
print("Stale:", stale_count)
print("Juveniles (open):", juveniles)
print("Oldest open:", oldest_name, oldest_year)