"""FastAPI web application with SSE streaming for the CrossGen pipeline."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse

from crossgen.pipeline import run_pipeline_streaming

BASE_DIR = Path(__file__).parent

app = FastAPI(title="CrossGen", description="Cross-Domain Idea Generator")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/solve", response_class=HTMLResponse)
async def solve_page(request: Request):
    return templates.TemplateResponse("solve.html", {"request": request})


@app.get("/api/solve")
async def api_solve(problem: str, model: str = "claude-sonnet-4-6"):
    """SSE endpoint: streams pipeline stage updates."""

    async def event_generator():
        try:
            async for update in run_pipeline_streaming(problem, model=model):
                yield {
                    "event": update.get("stage", "update"),
                    "data": json.dumps(update, default=str),
                }
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}),
            }

    return EventSourceResponse(event_generator())


@app.post("/api/solve")
async def api_solve_post(request: Request):
    """POST endpoint for solving (non-streaming, returns full result)."""
    from crossgen.pipeline import run_pipeline

    body = await request.json()
    problem = body.get("problem", "")
    model = body.get("model", "claude-sonnet-4-6")

    if not problem:
        return {"error": "No problem provided"}

    result = await run_pipeline(problem, model=model)
    return result.model_dump()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
