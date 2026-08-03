SELECT extract(dow from time) AS dow, count(*) AS earthquake_count
FROM earthquakes
GROUP BY dow
ORDER BY dow;
