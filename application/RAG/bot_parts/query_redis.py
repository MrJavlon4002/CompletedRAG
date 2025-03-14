import redis
import json

def get_redis_connection():
    return redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

def get_redis_session_history(session_id: str, **kwargs):
    r = get_redis_connection()
    try:
        history = r.get(f"chat:{session_id}")
        return json.loads(history) if history else []
    except redis.ConnectionError as e:
        print(f"Redis connection error in get_redis_session_history: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON decode error in get_redis_session_history: {e}")
        return []

def append_to_session_history(session_id: str, user_input: str, assistant_response: str, expiration_time: int = 3600, **kwargs):
    r = get_redis_connection()
    try:
        history = get_redis_session_history(session_id)
        history.append({"user_input": user_input, "assistant_response": assistant_response})
        r.setex(f"chat:{session_id}", expiration_time, json.dumps(history))
    except redis.ConnectionError as e:
        print(f"Redis connection error in append_to_session_history: {e}")