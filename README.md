
# Python tool
This app is a example of a tool for running Python code on a remote end point using a API.
It is made to be used with gpt-oss and to compatible with its native tool calling.

This is basicly a FastAPI wrapper for running Python code, but with session memory and automatic cleanup.
This makes it a 'fairly' safe enviroment for your llm to play in, but not unbreakable. If run as a Docker container, this possible breakage will be limmited to the container itself.

## Running
```bash
git clone https://github.com/lupusmagist/python-tool.git
cd python-tool
docker compose up --build -d
```

### Check logs:
docker logs -f python_tool

### Test
curl -X POST http://localhost:8081/python_tool \
  -H "Content-Type: application/json" \
  -d '{"code": "x = 5; print(x*2)"}'

## Re-use session
curl -X POST http://localhost:8081/python_tool \
  -H "Content-Type: application/json" \
  -d '{"code": "print(x + 3)", "session_id": "your-session-id"}'

#### List sessions
curl http://localhost:8081/python_tool/list_sessions

#### Cleanup sessions
curl -X POST http://localhost:8081/python_tool/timeout_cleanup

## Running without Docker
```bash
git clone https://github.com/lupusmagist/python-tool.git
cd python-tool
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn
uvicorn python_tool:app --host 0.0.0.0 --port 8081
```

