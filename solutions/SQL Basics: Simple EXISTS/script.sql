SELECT d.*
FROM departments d
WHERE EXISTS (
  SELECT *
  FROM sales s
  WHERE d.id = s.department_id
  AND price > 98
);
