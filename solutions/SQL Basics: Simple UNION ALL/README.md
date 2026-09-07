# SQL Basics: Simple UNION ALL
For this challenge you need to create a **UNION** statement. There are two
tables, `ussales` and `eusales`. The parent company tracks each sale at its
respective location's corresponding table; you must filter by the sale price so
the query returns only rows corresponding to a sale greater than `50.00`. You
have been tasked with combining that data for future analysis. Order by
**location** (US before EU), then by `id`.

### `ussales` / `eusales` table schema
- id
- name
- price
- card_name
- card_number
- transaction_date

### Resultant table schema
- location (EU for eusales and US for ussales)
- id
- name
- price (greater than 50.00)
- card_name
- card_number
- transaction_date

**Note:** The solution should use pure SQL.
