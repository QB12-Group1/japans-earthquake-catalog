SELECT month,
       region ,
       category,
       COUNT(*) AS count,
       round(AVG(mag)::NUMERIC , 2)::FLOAT as avg_mag,
       round(AVG(depth)::NUMERIC , 2)::FLOAT as avg_depth
FROM earthquakes
GROUP BY month , region , category;
