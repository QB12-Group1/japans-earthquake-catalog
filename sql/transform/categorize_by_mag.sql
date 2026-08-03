ALTER TABLE earthquakes
ADD COLUMN category TEXT;

UPDATE earthquakes
SET category = CASE
                   WHEN mag < 4 THEN 'Weak'
                   WHEN mag >= 4 AND mag <= 6 THEN 'Moderate'
                   WHEN mag > 6 THEN 'Strong'
    END ;
