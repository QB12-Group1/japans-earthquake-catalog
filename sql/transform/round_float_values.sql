UPDATE earthquakes
SET latitude  = round(latitude::NUMERIC, 1)::FLOAT,
    longitude = round(longitude::NUMERIC, 1)::FLOAT,
    depth     = round(depth::NUMERIC, 1)::FLOAT,
    mag       = round(mag::NUMERIC, 1)::FLOAT
WHERE latitude IS NOT NULL
  AND longitude IS NOT NULL
  AND depth IS NOT NULL
  AND mag IS NOT NULL;
