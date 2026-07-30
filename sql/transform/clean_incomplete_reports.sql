DELETE
FROM earthquakes
WHERE latitude IS NULL
   OR longitude IS NULL
   OR depth IS NULL
   OR mag IS NULL;
