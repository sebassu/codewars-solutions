SELECT MIN(score) AS min,
MAX(score) AS max,
PERCENTILE_CONT(0.5)
WITHIN GROUP (ORDER BY score)
AS median
FROM result;
