# codewars-solutions

Each folder under `solutions/` holds a kata's statement as `README.md` next to the solution file(s).

## Recording a solution

Run `scripts/add_solution.py <kata URL>` (`--username` overrides the default CodeWars
username). The script writes the folder and a draft `README.md` from the CodeWars API,
waits while you add the solution file(s) and touch up the README, then commits the folder
dated at the kata's completion time.
