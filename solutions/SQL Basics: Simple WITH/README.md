# SQL Basics: Simple WITH

For this challenge you need to create a `SELECT` statement that will use an `IN` to
check whether a department has had a sale with a price over **90.00 dollars**. The SQL
statement must use the `WITH` statement, which will be used to select all columns from
`sales` where the price is greater than $90.00$; you must call this sub-query
`special_sales`.

### `departments` table schema

- `id`
- `name`

### `sales` table schema

- `id`
- `department_id`
- `name`
- `price`
- `card_name`
- `card_number`
- `transaction_date`

### Resultant table schema

- `id`
- `name`

**Note:** Your solution should use pure SQL.
