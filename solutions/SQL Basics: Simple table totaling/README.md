# [SQL Basics: Simple table totaling](https://www.codewars.com/kata/5809575e166583acfa000083)

For this challenge you need to create a simple query to display each unique clan, with
their total points, and ranked by their total points.

### `people` table schema

- `name`
- `points`
- `clan`

### Resultant table schema

- `rank`
- `clan`
- `total_points`
- `total_people`

The query must rank each clan by their `total_points`. You must return each unqiue clan
and if there is no clan name (i.e. it's an empty string) you must replace it with
`"[no clan specified]"`. You must sum the `total_points` for each clan and the
`total_people` within that clan.

**Notes:**

- The data is loaded from the live leaderboard. This means values will chang,
  but also could cause the kata to time out retreiving the information.
- Your solution should use pure SQL.
