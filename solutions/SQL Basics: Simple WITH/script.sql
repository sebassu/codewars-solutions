WITH special_sales AS (
  SELECT DISTINCT department_id AS id
  FROM sales s
  WHERE s.price > 90
)
SELECT d.*
FROM special_sales s
INNER JOIN departments d
ON s.id = d.id;
