from typing import Callable, Dict, List

from .database import CachingDatabaseWrapper, Database, Optional, Transaction

class SerialTransactionExecutor:
    def __init__(self, db: 'SerialDatabase', txn: Transaction) -> None:
        self.db = db
        self.cached_db = CachingDatabaseWrapper(db)
        self.txn = txn
        self.start_tn = self.db._get_tnc()

    def read_phase(self) -> None:
        self.txn(self.cached_db)

    def validate_and_write_phase(self) -> bool:
        finish_tn = self.db._get_tnc()
        for tn in range(self.start_tn + 1, finish_tn + 1):
            cached_db = self.db._get_transaction(tn)
            write_set = cached_db.get_write_set()
            read_set = self.cached_db.get_read_set()
            if not write_set.isdisjoint(read_set):
                return False
        self.db._commit_transaction(self.cached_db)
        return True

class SerialDatabase(Database):
    def __init__(self) -> None:
        Database.__init__(self)
        self.transactions: Dict[int, CachingDatabaseWrapper] = {}
        self.tnc: int = 0

    def _get_tnc(self) -> int:
        return self.tnc

    def _get_transaction(self, tn: int) -> CachingDatabaseWrapper:
        assert tn in self.transactions
        return self.transactions[tn]

    def _commit_transaction(self, db: CachingDatabaseWrapper) -> None:
        self.tnc += 1
        assert self.tnc not in self.transactions
        self.transactions[self.tnc] = db
        db.commit()

    def begin(self, txn: Transaction) -> SerialTransactionExecutor:
        return SerialTransactionExecutor(self, txn)

def main():
    def init(db: CachingDatabaseWrapper) -> None:
        db.write('x', 0)
        db.write('y', 0)
        db.write('z', 0)

    def incr_vars(vs: List[str]) -> Transaction:
        def txn(db: CachingDatabaseWrapper) -> None:
            for v in vs:
                x = db.read(v)
                db.write(v, x + 1)
        return txn

    incr_x = incr_vars(['x'])
    incr_y = incr_vars(['y'])
    incr_z = incr_vars(['z'])
    incr_all = incr_vars(['x', 'y', 'z'])

    db = SerialDatabase()
    assert(db.data == {})

    t_init = db.begin(init)
    t_init.read_phase()
    assert(t_init.validate_and_write_phase())
    assert(db.data == {'x': 0, 'y': 0, 'z': 0})

    # t_1 and t_2 run concurrently and have conflicting read and write sets, so
    # whichever transaction attempts to commit first (i.e. t_1) succeeds. The
    # other (i.e. t_2) fails and is forced to abort.
    t_1 = db.begin(incr_all)
    t_2 = db.begin(incr_all)
    t_1.read_phase()
    t_2.read_phase()
    assert(t_1.validate_and_write_phase())
    assert(not t_2.validate_and_write_phase())
    assert(db.data == {'x': 1, 'y': 1, 'z': 1})

    # t_3 and t_4 run concurrently, but have disjoint read and write sets, so
    # they can both commit.
    t_3 = db.begin(incr_x)
    t_4 = db.begin(incr_y)
    t_3.read_phase()
    t_4.read_phase()
    assert(t_3.validate_and_write_phase())
    assert(t_4.validate_and_write_phase())
    assert(db.data == {'x': 2, 'y': 2, 'z': 1})

if __name__ == '__main__':
    main()
