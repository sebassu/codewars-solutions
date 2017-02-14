# SQL Basics: Simple JOIN
For this challenge you need to create a `SELECT` statement that will contain data
about `departments` that had a sale with a `price` over **98.00 dollars**. This `SELECT`
statement will have to use an `EXISTS` to achieve the task.

### `departments` table schema
- id
- name

### `sales` table schema
- id
- department_id _(foreign key)_
- name
- price
- card_name
- card_number
- transaction_date

### Resultant table schema
- id
- name

**Note:** Your solution should use pure SQL.
