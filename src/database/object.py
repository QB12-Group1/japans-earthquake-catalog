from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import NamedTuple

import psycopg2
from psycopg2.extras import NamedTupleCursor


class Database:
    def __init__(self, url: str) -> None:
        url = url.replace("+psycopg2", "")
        self._connection = psycopg2.connect(url)
        self._cursor = self._connection.cursor(cursor_factory=NamedTupleCursor)

    def run(self, query: str, params=()) -> None:
        self._cursor.execute(query, params)

    def run_many(self, query: str, params=()) -> None:
        self._cursor.executemany(query, params)

    def one(self, query: str, params=()) -> NamedTuple | None:
        self._cursor.execute(query, params)
        return self._cursor.fetchone()

    def all(self, query: str, params=()) -> list[NamedTuple]:
        self._cursor.execute(query, params)
        return self._cursor.fetchall()

    def commit(self) -> None:
        self._connection.commit()

    def rollback(self) -> None:
        self._connection.rollback()

    @contextmanager
    def transaction(self) -> Iterator[Database]:
        try:
            yield self
            self.commit()
        except Exception:
            self.rollback()
            raise

    def close(self) -> None:
        self._connection.close()
