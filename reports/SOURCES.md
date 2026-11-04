# Sources

- Murder Accountability Project, UCR homicide and clearance data (UCR65_25), murderdata.org, accessed 2026-11-04.
  Used for `dallas_series.csv` and `clearance_trend.png`. "Cleared" is the FBI definition: arrest or exceptional means.
- The Washington Post, Unsolved Homicide Database, github.com/washingtonpost/data-homicides, 2018. License: CC BY-NC-SA 4.0.
  Used for `dallas_map.html`. The Post counts a case as solved only when it is closed by arrest.

The two sources use different definitions of "cleared," so their numbers should not be compared without saying so.
Aggregate analysis only. Victim names are dropped on load and never appear in any output.
