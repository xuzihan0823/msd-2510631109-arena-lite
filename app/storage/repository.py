import json
import sqlite3
import uuid
from typing import Any


STUDENT_ID = "2510631109"


class DuplicateVoteError(ValueError):
    """Raised when a voter tries to add a second Vote to one Battle."""


class ArenaStore:
    """Single-process SQLite repository used by the course MVP."""

    def __init__(self) -> None:
        # FastAPI executes sync route handlers in worker threads. This course MVP
        # is single-process and explicitly out of scope for concurrent writes.
        self.connection = sqlite3.connect(":memory:", check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self._create_schema()
        self._seed_demo_data()

    def _create_schema(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE contestants (
                model_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                elo INTEGER NOT NULL,
                wins INTEGER NOT NULL DEFAULT 0,
                losses INTEGER NOT NULL DEFAULT 0,
                draws INTEGER NOT NULL DEFAULT 0,
                battles INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE battles (
                battle_id TEXT PRIMARY KEY,
                prompt TEXT NOT NULL,
                contestant_a_id TEXT NOT NULL,
                contestant_b_id TEXT NOT NULL,
                slot_a_id TEXT NOT NULL,
                slot_b_id TEXT NOT NULL,
                answer_a TEXT,
                answer_b TEXT,
                status TEXT NOT NULL,
                required_votes INTEGER NOT NULL DEFAULT 1,
                vote_count INTEGER NOT NULL DEFAULT 0,
                error_message TEXT,
                result_json TEXT
            );
            CREATE TABLE votes (
                vote_id TEXT PRIMARY KEY,
                battle_id TEXT NOT NULL,
                voter_id TEXT NOT NULL,
                choice TEXT NOT NULL CHECK(choice IN ('A', 'B')),
                UNIQUE(battle_id, voter_id)
            );
            CREATE TABLE status_events (
                event_id TEXT PRIMARY KEY,
                battle_id TEXT NOT NULL,
                from_status TEXT,
                to_status TEXT NOT NULL,
                reason TEXT
            );
            """
        )

    def _seed_demo_data(self) -> None:
        contestants = [
            (f"{STUDENT_ID}-model-alpha", "Model Alpha"),
            (f"{STUDENT_ID}-model-beta", "Model Beta"),
            (f"local-qwen-{STUDENT_ID}", "Local Qwen Demo"),
            (f"opencode-go-{STUDENT_ID}", "OpenCode Go Demo"),
        ]
        with self.connection:
            self.connection.executemany(
                """
                INSERT INTO contestants (model_id, name, elo, wins, losses, draws, battles)
                VALUES (?, ?, 1500, 0, 0, 0, 0)
                """,
                contestants,
            )

    @staticmethod
    def _as_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        return dict(row)

    def get_contestant(self, model_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT * FROM contestants WHERE model_id = ?", (model_id,)
        ).fetchone()
        return self._as_dict(row)

    def create_battle(
        self,
        prompt: str,
        contestant_a_id: str,
        contestant_b_id: str,
        slot_a_id: str,
        slot_b_id: str,
    ) -> str:
        battle_id = f"{STUDENT_ID}-battle-{uuid.uuid4().hex[:10]}"
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO battles (
                    battle_id, prompt, contestant_a_id, contestant_b_id,
                    slot_a_id, slot_b_id, status
                ) VALUES (?, ?, ?, ?, ?, ?, 'created')
                """,
                (battle_id, prompt, contestant_a_id, contestant_b_id, slot_a_id, slot_b_id),
            )
        return battle_id

    def get_battle(self, battle_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT * FROM battles WHERE battle_id = ?", (battle_id,)
        ).fetchone()
        battle = self._as_dict(row)
        if battle and battle["result_json"]:
            battle["result"] = json.loads(battle["result_json"])
        return battle

    def set_status(
        self,
        battle_id: str,
        from_status: str,
        to_status: str,
        reason: str | None = None,
    ) -> None:
        with self.connection:
            updated = self.connection.execute(
                """
                UPDATE battles
                SET status = ?, error_message = ?
                WHERE battle_id = ? AND status = ?
                """,
                (to_status, reason, battle_id, from_status),
            )
            if updated.rowcount != 1:
                raise ValueError("battle status changed unexpectedly")
            self.connection.execute(
                """
                INSERT INTO status_events (event_id, battle_id, from_status, to_status, reason)
                VALUES (?, ?, ?, ?, ?)
                """,
                (uuid.uuid4().hex, battle_id, from_status, to_status, reason),
            )

    def set_answers(self, battle_id: str, answer_a: str, answer_b: str) -> None:
        with self.connection:
            self.connection.execute(
                "UPDATE battles SET answer_a = ?, answer_b = ? WHERE battle_id = ?",
                (answer_a, answer_b, battle_id),
            )

    def has_vote(self, battle_id: str, voter_id: str) -> bool:
        row = self.connection.execute(
            "SELECT 1 FROM votes WHERE battle_id = ? AND voter_id = ?",
            (battle_id, voter_id),
        ).fetchone()
        return row is not None

    def add_vote(self, battle_id: str, voter_id: str, choice: str) -> str:
        vote_id = f"{STUDENT_ID}-vote-{uuid.uuid4().hex[:10]}"
        try:
            with self.connection:
                self.connection.execute(
                    "INSERT INTO votes (vote_id, battle_id, voter_id, choice) VALUES (?, ?, ?, ?)",
                    (vote_id, battle_id, voter_id, choice),
                )
                self.connection.execute(
                    "UPDATE battles SET vote_count = vote_count + 1 WHERE battle_id = ?",
                    (battle_id,),
                )
        except sqlite3.IntegrityError as error:
            raise DuplicateVoteError("a voter may vote only once per battle") from error
        return vote_id

    def vote_choice(self, battle_id: str) -> str | None:
        row = self.connection.execute(
            "SELECT choice FROM votes WHERE battle_id = ? ORDER BY rowid LIMIT 1", (battle_id,)
        ).fetchone()
        return None if row is None else str(row["choice"])

    def settle(
        self,
        battle_id: str,
        winner_id: str,
        loser_id: str,
        winner_elo: int,
        loser_elo: int,
        result: dict[str, Any],
    ) -> None:
        with self.connection:
            current = self.connection.execute(
                "SELECT status FROM battles WHERE battle_id = ?", (battle_id,)
            ).fetchone()
            if current is None or current["status"] != "voted":
                raise ValueError("battle is not ready to settle")
            self.connection.execute(
                """
                UPDATE contestants
                SET elo = ?, wins = wins + 1, battles = battles + 1
                WHERE model_id = ?
                """,
                (winner_elo, winner_id),
            )
            self.connection.execute(
                """
                UPDATE contestants
                SET elo = ?, losses = losses + 1, battles = battles + 1
                WHERE model_id = ?
                """,
                (loser_elo, loser_id),
            )
            self.connection.execute(
                """
                UPDATE battles SET status = 'scored', result_json = ?
                WHERE battle_id = ?
                """,
                (json.dumps(result, ensure_ascii=False), battle_id),
            )
            self.connection.execute(
                """
                INSERT INTO status_events (event_id, battle_id, from_status, to_status, reason)
                VALUES (?, ?, 'voted', 'scored', NULL)
                """,
                (uuid.uuid4().hex, battle_id),
            )

    def leaderboard(self, limit: int) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """
            SELECT model_id, name, elo, wins, losses, draws, battles
            FROM contestants
            ORDER BY elo DESC, model_id ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
