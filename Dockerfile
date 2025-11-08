FROM python:3.11-slim

WORKDIR /app
RUN pip install fastapi uvicorn

COPY app/python_tool.py ./python_tool.py

EXPOSE 8081
CMD ["uvicorn", "python_tool:app", "--host", "0.0.0.0", "--port", "8081"]
