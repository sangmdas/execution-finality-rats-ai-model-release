from __future__ import annotations

import sqlite3
import threading
import uuid
from pathlib import Path
from .models import Reservation


class StateError(RuntimeError):
    pass


class BudgetExhausted(StateError):
    pass


class EpochMismatch(StateError):
    pass


class InvalidReservation(StateError):
    pass


class SQLiteExtractionState:
    """
    Auditable software state store.

    Provides transactional atomicity and process-restart persistence, but does NOT
    claim hardware/VM snapshot anti-rollback. A production protected state backend
    must strengthen that property according to its assurance class.
    """

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        self._keeper = sqlite3.connect(self.path, timeout=30, isolation_level=None, check_same_thread=False)
        self._keeper.execute("PRAGMA foreign_keys=ON")
        if self.path != ":memory:":
            self._keeper.execute("PRAGMA journal_mode=WAL")
            self._keeper.execute("PRAGMA synchronous=FULL")
        self._init_schema(self._keeper)
        self._local_lock = threading.RLock()

    @staticmethod
    def _init_schema(conn: sqlite3.Connection) -> None:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS budgets (
                scope_key TEXT NOT NULL,
                release_class TEXT NOT NULL,
                epoch INTEGER NOT NULL,
                budget INTEGER NOT NULL CHECK (budget >= 0),
                consumed INTEGER NOT NULL DEFAULT 0 CHECK (consumed >= 0),
                PRIMARY KEY (scope_key, release_class)
            );

            CREATE TABLE IF NOT EXISTS reservations (
                reservation_id TEXT PRIMARY KEY,
                scope_key TEXT NOT NULL,
                release_class TEXT NOT NULL,
                candidate_digest TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                epoch INTEGER NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('RESERVED','COMMITTED','POISONED','CANCELLED')),
                authority_id TEXT UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scope_key, release_class)
                    REFERENCES budgets(scope_key, release_class)
            );
            CREATE INDEX IF NOT EXISTS idx_reservation_candidate
                ON reservations(candidate_digest, status);
            """
        )

    def _connect(self) -> sqlite3.Connection:
        if self.path == ":memory:":
            return self._keeper
        conn = sqlite3.connect(self.path, timeout=30, isolation_level=None, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=FULL")
        return conn

    def provision(self, scope_key: str, release_class: str, epoch: int, budget: int) -> None:
        if budget < 0 or epoch < 0:
            raise ValueError("budget and epoch must be non-negative")
        conn = self._connect()
        own = conn is not self._keeper
        try:
            with self._local_lock:
                conn.execute("BEGIN IMMEDIATE")
                row = conn.execute(
                    "SELECT consumed FROM budgets WHERE scope_key=? AND release_class=?",
                    (scope_key, release_class),
                ).fetchone()
                if row and row[0] > budget:
                    raise StateError("new budget would be below already-consumed quantity")
                conn.execute(
                    """
                    INSERT INTO budgets(scope_key, release_class, epoch, budget, consumed)
                    VALUES(?,?,?,?,COALESCE((SELECT consumed FROM budgets WHERE scope_key=? AND release_class=?),0))
                    ON CONFLICT(scope_key, release_class)
                    DO UPDATE SET epoch=excluded.epoch, budget=excluded.budget
                    """,
                    (scope_key, release_class, epoch, budget, scope_key, release_class),
                )
                conn.execute("COMMIT")
        except Exception:
            try: conn.execute("ROLLBACK")
            except sqlite3.Error: pass
            raise
        finally:
            if own: conn.close()

    def read(self, scope_key: str, release_class: str) -> dict[str, int]:
        conn = self._connect(); own = conn is not self._keeper
        try:
            row = conn.execute(
                "SELECT epoch,budget,consumed FROM budgets WHERE scope_key=? AND release_class=?",
                (scope_key, release_class),
            ).fetchone()
            if not row:
                raise StateError("unprovisioned scope/release_class")
            return {"epoch": row[0], "budget": row[1], "consumed": row[2], "remaining": row[1]-row[2]}
        finally:
            if own: conn.close()

    def reserve(self, *, scope_key: str, release_class: str, epoch: int, quantity: int, candidate_digest: str) -> Reservation:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        conn = self._connect(); own = conn is not self._keeper
        rid = str(uuid.uuid4())
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT epoch,budget,consumed FROM budgets WHERE scope_key=? AND release_class=?",
                (scope_key, release_class),
            ).fetchone()
            if not row:
                raise StateError("unprovisioned scope/release_class")
            current_epoch, budget, consumed = row
            if current_epoch != epoch:
                raise EpochMismatch(f"state epoch {current_epoch} != candidate epoch {epoch}")
            if consumed + quantity > budget:
                raise BudgetExhausted("protected extraction budget exhausted")

            # Reservation consumes capacity immediately. Cancellation may restore only
            # where the caller can prove no external effect occurred.
            updated = conn.execute(
                """
                UPDATE budgets SET consumed = consumed + ?
                WHERE scope_key=? AND release_class=? AND epoch=? AND consumed + ? <= budget
                """,
                (quantity, scope_key, release_class, epoch, quantity),
            )
            if updated.rowcount != 1:
                raise BudgetExhausted("concurrent reservation consumed the remaining authority")

            conn.execute(
                "INSERT INTO reservations(reservation_id,scope_key,release_class,candidate_digest,quantity,epoch,status) VALUES(?,?,?,?,?,?, 'RESERVED')",
                (rid, scope_key, release_class, candidate_digest, quantity, epoch),
            )
            conn.execute("COMMIT")
            return Reservation(rid, scope_key, release_class, candidate_digest, quantity, epoch, "RESERVED")
        except Exception:
            try: conn.execute("ROLLBACK")
            except sqlite3.Error: pass
            raise
        finally:
            if own: conn.close()

    def attach_authority(self, reservation_id: str, authority_id: str) -> None:
        conn = self._connect(); own = conn is not self._keeper
        try:
            conn.execute("BEGIN IMMEDIATE")
            cur = conn.execute(
                "UPDATE reservations SET authority_id=? WHERE reservation_id=? AND status='RESERVED' AND authority_id IS NULL",
                (authority_id, reservation_id),
            )
            if cur.rowcount != 1:
                raise InvalidReservation("reservation is not attachable")
            conn.execute("COMMIT")
        except Exception:
            try: conn.execute("ROLLBACK")
            except sqlite3.Error: pass
            raise
        finally:
            if own: conn.close()

    def reservation(self, reservation_id: str) -> dict[str, object]:
        conn = self._connect(); own = conn is not self._keeper
        try:
            row = conn.execute(
                "SELECT scope_key,release_class,candidate_digest,quantity,epoch,status,authority_id FROM reservations WHERE reservation_id=?",
                (reservation_id,),
            ).fetchone()
            if not row:
                raise InvalidReservation("unknown reservation")
            keys = ["scope_key","release_class","candidate_digest","quantity","epoch","status","authority_id"]
            return dict(zip(keys,row))
        finally:
            if own: conn.close()

    def commit(self, reservation_id: str, authority_id: str) -> None:
        """Consume the authority terminally before returning bytes to caller."""
        conn = self._connect(); own = conn is not self._keeper
        try:
            conn.execute("BEGIN IMMEDIATE")
            cur = conn.execute(
                """UPDATE reservations SET status='COMMITTED'
                   WHERE reservation_id=? AND authority_id=? AND status='RESERVED'""",
                (reservation_id, authority_id),
            )
            if cur.rowcount != 1:
                raise InvalidReservation("authority is stale, replayed, or not bound to reservation")
            conn.execute("COMMIT")
        except Exception:
            try: conn.execute("ROLLBACK")
            except sqlite3.Error: pass
            raise
        finally:
            if own: conn.close()

    def poison(self, reservation_id: str) -> None:
        conn = self._connect(); own = conn is not self._keeper
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "UPDATE reservations SET status='POISONED' WHERE reservation_id=? AND status='RESERVED'",
                (reservation_id,),
            )
            conn.execute("COMMIT")
        finally:
            if own: conn.close()

    def cancel_no_effect(self, reservation_id: str) -> None:
        """Restore capacity only when caller knows no external effect occurred."""
        conn = self._connect(); own = conn is not self._keeper
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT scope_key,release_class,quantity,status FROM reservations WHERE reservation_id=?",
                (reservation_id,),
            ).fetchone()
            if not row or row[3] != "RESERVED":
                raise InvalidReservation("only an unconsumed RESERVED reservation can be cancelled")
            conn.execute(
                "UPDATE budgets SET consumed=consumed-? WHERE scope_key=? AND release_class=? AND consumed>=?",
                (row[2], row[0], row[1], row[2]),
            )
            conn.execute("UPDATE reservations SET status='CANCELLED' WHERE reservation_id=?", (reservation_id,))
            conn.execute("COMMIT")
        except Exception:
            try: conn.execute("ROLLBACK")
            except sqlite3.Error: pass
            raise
        finally:
            if own: conn.close()

    def close(self) -> None:
        self._keeper.close()
