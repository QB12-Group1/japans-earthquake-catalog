CREATE OR REPLACE FUNCTION extract_region(place TEXT) RETURNS TEXT AS
$$
DECLARE
    region                 TEXT;
    DECLARE extracted_text TEXT;
BEGIN
    extracted_text = lower(place);
    extracted_text = regexp_replace(extracted_text, ',.+', '');
    extracted_text = regexp_replace(extracted_text, '.+,', '');
    extracted_text = regexp_replace(extracted_text, '.+of ', '');
    region = concat(extracted_text);
    region = trim(region);
    return initcap(region);
END;
$$ LANGUAGE plpgsql;

ALTER TABLE earthquakes
    ADD COLUMN region TEXT;
UPDATE earthquakes
SET region = extract_region(place)
WHERE place IS NOT NULL;
