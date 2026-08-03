SELECT extract(hour from time) AS hour, count(*) AS earthquake_count
FROM earthquakes
GROUP BY hour
ORDER BY hour;
