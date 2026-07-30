SELECT CASE
           WHEN mag < 4 THEN 'Weak'
           WHEN mag >= 4 AND mag <= 6 THEN 'Moderate'
           WHEN mag > 6 THEN 'Strong' END AS category, *
FROM earthquakes ORDER BY mag;
