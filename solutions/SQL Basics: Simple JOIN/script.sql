SELECT p.*, c.name AS company_name
FROM products p
INNER JOIN companies c
ON c.id = p.company_id;
