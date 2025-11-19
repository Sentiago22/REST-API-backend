from fastapi import FastAPI
import redis
import json
import random

ARRAY_KEY = "numbers_array"
ARRAY_SIZE = 100

app = FastAPI()

# Kết nối redis (host = tên service trong docker-compose)
r = redis.Redis(host="redis", port=6379, decode_responses=True)


def generate_array():
    data = [random.randint(0, 999) for _ in range(ARRAY_SIZE)]
    data.sort()
    return data


def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


@app.on_event("startup")
def startup_event():
    """Sinh mảng nếu chưa tồn tại trong Redis."""
    if not r.exists(ARRAY_KEY):
        arr = generate_array()
        r.set(ARRAY_KEY, json.dumps(arr))
        print("Generated new array and saved to Redis")
    else:
        print("Loaded existing array from Redis")


@app.get("/search/{value}")
def search(value: int):
    raw = r.get(ARRAY_KEY)
    arr = json.loads(raw)
    index = binary_search(arr, value)
    return {"value": value, "index": index}
