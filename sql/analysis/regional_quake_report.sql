WITH regional_report (r, ec, ad, am, mm, dd, sd) AS
         (SELECT region,
                 count(*),
                 avg(depth)::NUMERIC,
                 avg(mag)::NUMERIC,
                 max(mag)::NUMERIC,
                 max(depth)::NUMERIC,
                 min(depth)::NUMERIC
          FROM earthquakes
          GROUP BY region),
     readable_report (r, ec, ad, am, mm, dd, sd) AS
         (SELECT r, ec, round(ad, 2), round(am, 2), round(mm, 2), round(dd, 2), round(sd, 2) FROM regional_report)
SELECT r  AS region,
       ec AS earthquake_count,
       ad::FLOAT AS avg_depth,
       am::FLOAT AS avg_magnitude,
       mm::FLOAT AS max_magnitude,
       dd::FLOAT AS deepest_depth,
       sd::FLOAT AS shallowest_depth
FROM readable_report;
