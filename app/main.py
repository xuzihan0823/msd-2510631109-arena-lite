from fastapi import FastAPI

app = FastAPI(title="arena-lite")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
