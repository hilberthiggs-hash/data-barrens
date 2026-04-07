FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ server/

ENV ARENA_DB_PATH=/data/arena.db

EXPOSE 21520

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "21520"]
