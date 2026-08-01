WITH cte AS (SELECT lag(id) over (partition by region order by time)        as lid,
                    lag(time) over (partition by region order by time)      as ltime,
                    lag(place) over (partition by region order by time)     as lplace,
                    lag(region) over (partition by region order by time)    as lregion,
                    lag(latitude) over (partition by region order by time)  as llatitude,
                    lag(longitude) over (partition by region order by time) as llongitude,
                    lag(depth) over (partition by region order by time)     as ldepth,
                    lag(mag) over (partition by region order by time)       as lmag,
                    id                                                      as id,
                    time                                                    as time,
                    place                                                   as place,
                    region                                                  as region,
                    latitude                                                as latitude,
                    longitude                                               as longitude,
                    depth                                                   as depth,
                    mag                                                     as mag
             FROM earthquakes),
     diff_cte AS (SELECT *,
                         abs(extract(epoch from ltime) - extract(epoch from time)) as epoch_diff
                  FROM cte),
     candiates AS (SELECT id,
                          lid,
                          time,
                          ltime,
                          place,
                          lplace,
                          region,
                          lregion,
                          latitude,
                          llatitude,
                          longitude,
                          llongitude,
                          depth,
                          ldepth,
                          mag,
                          lmag
                   FROM diff_cte
                   WHERE epoch_diff <= 90),
     duplicate_candiates AS (SELECT row_number() over (partition by e.region order by e.time) AS row_number,
                                    e.id,
                                    e.time,
                                    e.latitude,
                                    e.longitude,
                                    e.depth,
                                    e.mag,
                                    e.place,
                                    e.source,
                                    e.region
                             FROM earthquakes AS e
                                      JOIN candiates AS d
                                           ON e.id = d.id OR
                                              e.id = d.lid),
     duplicate_candiates_diff AS (SELECT lag(time) over () as ldt,
                                         time              as cdt,
                                         *
                                  FROM duplicate_candiates),
     duplicates AS (SELECT *
                    FROM duplicate_candiates_diff
                    WHERE abs(extract(epoch from ldt) - extract(epoch from cdt)) <= 90
                      and row_number > 1)
DELETE
FROM earthquakes
WHERE id IN (SELECT id FROM duplicates);
