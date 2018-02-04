from typing import Any, Dict, Optional, Set, Callable

class Database:
    """
    A database is a mapping from string-valued keys to Any-valued values. Our
    database API is a bit different from the one presented in [1]. We perform
    reads and writes on entire objects, rather than on attributes within
    objects. We also remove the create, delete, copy, and exchange methods
    to keep things simple.

    [1]: https://scholar.google.com/scholar?cluster=14884990087876248723
    """
    def __init__(self) -> None:
        self.data: Dict[str, Any] = {}

    def __str__(self) -> str:
        return str(self.data)

    def write(self, name: str, val: Any) -> None:
        self.data[name] = val

    def read(self, name: str) -> Any:
        assert name in self.data
        return self.data[name]

class CachingDatabaseWrapper:
    """
    A CachingDatabaseWrapper provides the twrite/tread/tdelete interface
    described in [1]. A CachingDatabaseWrapper wrapper acts like a database,
    but writes are buffered in a local cache, and reads read from this cache
    (or the database, if the object being read hasn't been written).

    [1]: https://scholar.google.com/scholar?cluster=14884990087876248723
    """
    def __init__(self, db: Database) -> None:
        self.db = db
        self.copies: Dict[str, Any] = {}
        self.read_set: Set[str] = set()

    def write(self, name: str, val: Any) -> None:
        self.copies[name] = val

    def read(self, name: str) -> Any:
        self.read_set.add(name)
        if name in self.copies:
            return self.copies[name]
        else:
            return self.db.read(name)

    def commit(self) -> None:
        for k, v in self.copies.items():
            self.db.write(k, v)

    def get_write_set(self) -> Set[str]:
        return set(self.copies.keys())

    def get_read_set(self) -> Set[str]:
        return self.read_set

Transaction = Callable[[CachingDatabaseWrapper], None]
