import pandas as pd
from sqlalchemy import text

from config.settings import BASE_DIR
from src.database.session import get_session


def create_table() -> None:
    schema_path = BASE_DIR / "sql" / "schema.sql"
    with open(schema_path) as file, get_session() as session:
        schema = text(file.read())
        session.execute(schema)
        session.commit()


def drop_table() -> None:
    with get_session() as session:
        query = text("DROP TABLE IF EXISTS earthquakes")
        session.execute(query)
        session.commit()


def load_to_sql(df: pd.DataFrame) -> None:
    with get_session() as session:
        try:
            session.begin()
            df.to_sql(
                "earthquakes",
                session.bind,
                chunksize=100,
                if_exists="append",
                index=False,
            )
        except Exception:
            session.rollback()
            raise
