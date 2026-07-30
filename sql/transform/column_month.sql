ALTER TABLE earthquakes
ADD COLUMN month INTEGER;

UPDATE earthquakes
SET month = date_part('month',time);
