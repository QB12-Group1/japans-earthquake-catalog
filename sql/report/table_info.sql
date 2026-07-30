CREATE OR REPLACE FUNCTION get_table_profile()
    RETURNS TABLE
            (
                col_count     BIGINT,
                col_name      VARCHAR,
                col_type      VARCHAR,
                total_records BIGINT
            )
    LANGUAGE plpgsql
AS
$$
DECLARE
    row_count    BIGINT;
    column_count BIGINT;
BEGIN
    -- Get the record count once
    SELECT COUNT(*) INTO row_count FROM earthquakes;
    SELECT COUNT(*) INTO column_count FROM information_schema.columns where table_name = 'earthquakes';


    -- Return a set of rows, joining columns with the record count
    RETURN QUERY
        SELECT column_count,
               column_name::VARCHAR,
               data_type::VARCHAR,
               row_count
        FROM information_schema.columns
        WHERE table_name = 'earthquakes';
END;
$$;

SELECT *
FROM get_table_profile();
