import os
import socket

import redis
from flask import Flask, jsonify

app = Flask(__name__)

# Shared state store: every app replica talks to the same Redis,
# so the counter stays consistent no matter which instance serves the request.
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,
)

INSTANCE_ID = socket.gethostname()


@app.route("/")
def home():
    total = redis_client.incr("total_hits")
    redis_client.hincrby("hits_per_instance", INSTANCE_ID, 1)
    return jsonify(message="Hello from the cluster!", instance=INSTANCE_ID, total_hits=total)


@app.route("/health")
def health():
    return jsonify(status="ok", instance=INSTANCE_ID)


@app.route("/add/<int:a>/<int:b>")
def add(a, b):
    return jsonify(result=a + b, instance=INSTANCE_ID)


@app.route("/stats")
def stats():
    per_instance = redis_client.hgetall("hits_per_instance")
    return jsonify(
        total_hits=int(redis_client.get("total_hits") or 0),
        per_instance={k: int(v) for k, v in per_instance.items()},
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
