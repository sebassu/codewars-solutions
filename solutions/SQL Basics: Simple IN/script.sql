SELECT d.*
FROM departments d
WHERE d.Id IN (
  SELECT s.department_id
  FROM sales s
  WHERE price > 98
);
