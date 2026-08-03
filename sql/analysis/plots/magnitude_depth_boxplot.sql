SELECT mag AS magnitude ,
       CASE
           WHEN depth <= 50 THEN 'Shallow'
           WHEN depth <= 250 THEN 'Intermediate'
           ELSE 'Deep'
           END AS depth_group
FROM earthquakes;
