from fastapi import FastAPI, Request
import io, contextlib, traceback, uuid, asyncio, time

app = FastAPI(title="Stateful Python Tool")

# Store sessions in memory: {session_id: {"globals": dict, "last_used": float}}
sessions = {}

# Configurable constants
EXECUTION_TIMEOUT = 3.0  # seconds per code cell
SESSION_TTL = 600        # 10 minutes idle before cleanup

# Auto session cleanup
@app.on_event("startup")
async def start_cleanup_task():
    async def periodic_cleanup():
        while True:
            await asyncio.sleep(120)
            await timeout_cleanup()
    asyncio.create_task(periodic_cleanup())

@app.post("/python_tool")
async def python_tool(request: Request):
    """
    Execute Python code in a persistent session.
    Each session retains its own global context.
    """
    body = await request.json()
    code = body.get("code", "")
    session_id = body.get("session_id") or str(uuid.uuid4())

    # Retrieve or initialize a session
    session = sessions.setdefault(session_id, {"globals": {}, "last_used": time.time()})
    context = session["globals"]
    session["last_used"] = time.time()

    stdout = io.StringIO()
    result = {"session_id": session_id, "stdout": "", "error": ""}

    async def run_code():
        with contextlib.redirect_stdout(stdout):
            exec(code, context)

    try:
        await asyncio.wait_for(run_code(), timeout=EXECUTION_TIMEOUT)
        result["stdout"] = stdout.getvalue().strip()
    except asyncio.TimeoutError:
        result["error"] = f"Execution timed out after {EXECUTION_TIMEOUT} seconds."
    except Exception:
        result["error"] = traceback.format_exc()

    return result


@app.post("/python_tool/reset")
async def reset_session(request: Request):
    """Delete one session by ID."""
    body = await request.json()
    session_id = body.get("session_id")
    if session_id and session_id in sessions:
        del sessions[session_id]
        return {"message": f"Session {session_id} reset."}
    return {"message": "Session not found."}


@app.get("/python_tool/list_sessions")
async def list_sessions():
    """List all current sessions and their last activity times."""
    now = time.time()
    data = [
        {
            "session_id": sid,
            "last_used_seconds_ago": round(now - s["last_used"], 1),
            "globals": [k for k in s["globals"].keys() if not k.startswith("__")]
        }
        for sid, s in sessions.items()
    ]
    return {"active_sessions": data}


@app.post("/python_tool/timeout_cleanup")
async def timeout_cleanup():
    """Delete sessions idle longer than SESSION_TTL."""
    now = time.time()
    removed = []
    for sid, s in list(sessions.items()):
        if now - s["last_used"] > SESSION_TTL:
            del sessions[sid]
            removed.append(sid)
    return {"removed_sessions": removed, "remaining_sessions": list(sessions.keys())}


