SELECT source , region , round(AVG(mag)::NUMERIC , 2) AS Average
FROM earthquakes
GROUP BY source , region
ORDER BY Average DESC;
