SELECT month , count(*) AS count
FROM earthquakes
GROUP BY month
ORDER BY month;
