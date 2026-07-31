SELECT month , count(*)
FROM earthquakes
GROUP BY month
ORDER BY month;
