SELECT source , region , round(AVG(mag)::NUMERIC , 2)::FLOAT AS Average
FROM earthquakes
GROUP BY source , region
ORDER BY Average DESC;
