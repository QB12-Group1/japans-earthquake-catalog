import pandas as pd

from src.database.session import get_session


def load_to_sql(df: pd.DataFrame) -> None:
    with get_session() as session:
        try:
            session.begin()
            df.to_sql(
                "earthquakes",
                session.bind,
                chunksize=100,
                if_exists="replace",
                index=False,
            )
        except Exception:
            session.rollback()
            raise
