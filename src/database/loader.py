import pandas as pd
from sqlalchemy import text

from src.database.session import get_session


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
