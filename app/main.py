from typing import Any

from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.adapters.models import MockModelAdapter
from app.domain.battle import IllegalStateTransition, transition
from app.domain.elo import update_elo
from app.domain.pairing import SameContestantError, assign_slots, validate_distinct_contestants
from app.storage.repository import ArenaStore, DuplicateVoteError


STUDENT_ID = "2510631109"
TOKENS = {
    "local-admin-token": "admin",
    "local-voter-token": "voter",
}


class LoginRequest(BaseModel):
    role: str = ""


class CreateBattleRequest(BaseModel):
    prompt: str = ""
    contestant_a_id: str | None = None
    contestant_b_id: str | None = None
    contestant_a: str | None = None
    contestant_b: str | None = None

    @property
    def left_contestant(self) -> str | None:
        return self.contestant_a_id or self.contestant_a

    @property
    def right_contestant(self) -> str | None:
        return self.contestant_b_id or self.contestant_b


class VoteRequest(BaseModel):
    choice: str | None = None


app = FastAPI(title="arena-lite")
app.state.store = ArenaStore()
app.state.adapter = MockModelAdapter()


def reset_for_tests() -> None:
    """Reset the single-process demo state between API tests."""
    app.state.store = ArenaStore()
    app.state.adapter = MockModelAdapter()


def _store() -> ArenaStore:
    return app.state.store


def _adapter() -> MockModelAdapter:
    return app.state.adapter


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


def _has_role(authorization: str | None, expected_role: str) -> bool:
    if not authorization or not authorization.startswith("Bearer "):
        return False
    token = authorization.removeprefix("Bearer ")
    return TOKENS.get(token) == expected_role


def _auth_error() -> JSONResponse:
    return _error(401, f"AUTH_REQUIRED_{STUDENT_ID}", "需要匹配角色的本地测试身份")


def _battle_or_404(battle_id: str) -> tuple[dict[str, Any] | None, JSONResponse | None]:
    battle = _store().get_battle(battle_id)
    if battle is None:
        return None, _error(404, f"BATTLE_NOT_FOUND_{STUDENT_ID}", "battle 不存在")
    return battle, None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/login")
def login(request: LoginRequest) -> Any:
    if request.role == "admin":
        return {"token": "local-admin-token", "role": "admin"}
    if request.role == "voter":
        return {"token": "local-voter-token", "role": "voter"}
    return _auth_error()


@app.post("/battles", status_code=201)
def create_battle(
    request: CreateBattleRequest,
    authorization: str | None = Header(default=None),
) -> Any:
    if not _has_role(authorization, "admin"):
        return _auth_error()

    prompt = request.prompt.strip()
    contestant_a_id = request.left_contestant
    contestant_b_id = request.right_contestant
    if not prompt or len(prompt) > 2000:
        return _error(
            422,
            f"INVALID_PROMPT_{STUDENT_ID}",
            "prompt 不能为空且长度不得超过 2000",
        )
    if not contestant_a_id or not contestant_b_id:
        return _error(422, f"INVALID_CONTESTANT_{STUDENT_ID}", "需要两个 contestant")
    try:
        validate_distinct_contestants(contestant_a_id, contestant_b_id)
    except SameContestantError:
        return _error(
            422,
            f"SAME_CONTESTANT_{STUDENT_ID}",
            "两个 contestant 必须不同",
        )

    store = _store()
    if store.get_contestant(contestant_a_id) is None or store.get_contestant(contestant_b_id) is None:
        return _error(422, f"UNKNOWN_CONTESTANT_{STUDENT_ID}", "contestant 不存在")

    slot_a_id, slot_b_id = assign_slots(contestant_a_id, contestant_b_id)
    battle_id = store.create_battle(
        prompt,
        contestant_a_id,
        contestant_b_id,
        slot_a_id,
        slot_b_id,
    )
    transition("created", "answering")
    store.set_status(battle_id, "created", "answering")

    answer_a = _adapter().ask(slot_a_id, prompt, 1.0)
    answer_b = _adapter().ask(slot_b_id, prompt, 1.0)
    failed = next(
        (
            answer
            for answer in (answer_a, answer_b)
            if answer.error_type != "none" or not answer.text.strip()
        ),
        None,
    )
    if failed is not None:
        reason = failed.error_type if failed.error_type != "none" else "empty_response"
        transition("answering", "aborted")
        store.set_status(battle_id, "answering", "aborted", reason)
    else:
        store.set_answers(battle_id, answer_a.text, answer_b.text)
        transition("answering", "ready")
        store.set_status(battle_id, "answering", "ready")

    # The response preserves the observable created -> answering transition;
    # mock completion is synchronous, so an immediate GET observes ready/aborted.
    return {"battle_id": battle_id, "status": "answering"}


@app.get("/battles/{battle_id}")
def get_battle(
    battle_id: str,
    authorization: str | None = Header(default=None),
) -> Any:
    if not _has_role(authorization, "voter"):
        return _auth_error()
    battle, error = _battle_or_404(battle_id)
    if error is not None:
        return error
    assert battle is not None

    response: dict[str, Any] = {
        "battle_id": battle["battle_id"],
        "status": battle["status"],
        "question": battle["prompt"],
        "vote_count": battle["vote_count"],
        "required_votes": battle["required_votes"],
    }
    if battle["status"] == "aborted":
        response["error_message"] = battle["error_message"]
        return response

    response["answer_a"] = battle["answer_a"]
    response["answer_b"] = battle["answer_b"]
    if battle["status"] == "scored":
        result = battle.get("result", {})
        response["result"] = result
        response["votes"] = result.get("vote_counts", {})
        response["elo_before"] = result.get("elo_before", {})
        response["elo_after"] = result.get("elo_after", {})
        response["elo_delta"] = result.get("elo_delta", {})
    return response


@app.post("/battles/{battle_id}/vote")
def vote(
    battle_id: str,
    request: VoteRequest,
    authorization: str | None = Header(default=None),
) -> Any:
    if not _has_role(authorization, "voter"):
        return _auth_error()
    battle, error = _battle_or_404(battle_id)
    if error is not None:
        return error
    assert battle is not None
    if request.choice not in {"A", "B"}:
        return _error(422, f"INVALID_CHOICE_{STUDENT_ID}", "choice 只能为 A 或 B")

    voter_id = f"{STUDENT_ID}-user-demo"
    if battle["status"] != "ready":
        if battle["status"] == "voted" and _store().has_vote(battle_id, voter_id):
            return _error(409, f"ALREADY_VOTED_{STUDENT_ID}", "同一 voter 只能投票一次")
        return _error(409, f"ILLEGAL_STATE_{STUDENT_ID}", "battle 当前状态不可投票")
    try:
        vote_id = _store().add_vote(battle_id, voter_id, request.choice)
    except DuplicateVoteError:
        return _error(409, f"ALREADY_VOTED_{STUDENT_ID}", "同一 voter 只能投票一次")

    try:
        transition("ready", "voted")
        _store().set_status(battle_id, "ready", "voted")
    except IllegalStateTransition:
        return _error(409, f"ILLEGAL_STATE_{STUDENT_ID}", "battle 当前状态不可投票")
    updated, _ = _battle_or_404(battle_id)
    assert updated is not None
    return {
        "battle_id": battle_id,
        "vote_id": vote_id,
        "choice": request.choice,
        "vote_count": updated["vote_count"],
        "required_votes": updated["required_votes"],
        "status": updated["status"],
    }


@app.post("/battles/{battle_id}/settle")
def settle(
    battle_id: str,
    authorization: str | None = Header(default=None),
) -> Any:
    if not _has_role(authorization, "admin"):
        return _auth_error()
    battle, error = _battle_or_404(battle_id)
    if error is not None:
        return error
    assert battle is not None
    if battle["status"] != "voted":
        return _error(409, f"ILLEGAL_STATE_{STUDENT_ID}", "battle 当前状态不可结算")

    choice = _store().vote_choice(battle_id)
    if choice not in {"A", "B"}:
        return _error(409, f"ILLEGAL_STATE_{STUDENT_ID}", "battle 尚未达到投票阈值")
    slot_a = _store().get_contestant(str(battle["slot_a_id"]))
    slot_b = _store().get_contestant(str(battle["slot_b_id"]))
    assert slot_a is not None and slot_b is not None
    rating_update = update_elo(slot_a["elo"], slot_b["elo"], winner=choice)
    winner_id = str(battle["slot_a_id"] if choice == "A" else battle["slot_b_id"])
    loser_id = str(battle["slot_b_id"] if choice == "A" else battle["slot_a_id"])
    result = {
        "reveal": {
            "answer_a_contestant": battle["slot_a_id"],
            "answer_b_contestant": battle["slot_b_id"],
        },
        "vote_counts": {"A": 1 if choice == "A" else 0, "B": 1 if choice == "B" else 0},
        "elo_before": {battle["slot_a_id"]: slot_a["elo"], battle["slot_b_id"]: slot_b["elo"]},
        "elo_after": {battle["slot_a_id"]: rating_update.rating_a, battle["slot_b_id"]: rating_update.rating_b},
        "elo_delta": {battle["slot_a_id"]: rating_update.delta_a, battle["slot_b_id"]: rating_update.delta_b},
    }
    _store().settle(
        battle_id,
        winner_id,
        loser_id,
        rating_update.rating_a if choice == "A" else rating_update.rating_b,
        rating_update.rating_b if choice == "A" else rating_update.rating_a,
        result,
    )
    return {"battle_id": battle_id, "status": "scored", **result}


@app.get("/leaderboard")
def leaderboard(
    authorization: str | None = Header(default=None),
    limit: int = 20,
) -> Any:
    if not _has_role(authorization, "voter"):
        return _auth_error()
    if not 1 <= limit <= 100:
        return _error(422, f"INVALID_LIMIT_{STUDENT_ID}", "limit 必须在 1 到 100 之间")
    rows = _store().leaderboard(limit)
    items = [{"rank": index, **row} for index, row in enumerate(rows, start=1)]
    return {"items": items}