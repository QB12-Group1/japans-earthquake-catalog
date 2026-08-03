ALTER TABLE earthquakes
ADD COLUMN month INTEGER;

UPDATE earthquakes
SET month = DATE_PART('month',time);
