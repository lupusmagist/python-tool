
docker compose up --build -d

# Check logs:
docker logs -f python_tool

# Test
curl -X POST http://localhost:8081/python_tool \
  -H "Content-Type: application/json" \
  -d '{"code": "x = 5; print(x*2)"}'

## Re-use session
curl -X POST http://localhost:8081/python_tool \
  -H "Content-Type: application/json" \
  -d '{"code": "print(x + 3)", "session_id": "your-session-id"}'

## List sessions
curl http://localhost:8081/python_tool/list_sessions

## Cleanup sessions
curl -X POST http://localhost:8081/python_tool/timeout_cleanup