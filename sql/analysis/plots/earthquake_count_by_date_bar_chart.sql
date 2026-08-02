WITH cte AS (SELECT id, extract(day from time) AS day
             FROM earthquakes)
SELECT e.time AS time, day, count(*) AS earthquake_count
FROM earthquakes AS e
         JOIN cte ON e.id = cte.id
GROUP BY day, time ORDER BY day;
