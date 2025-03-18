import redis
import json

def get_redis_connection():
    try:
        return redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
    except redis.ConnectionError as e:
        print(str(e))


def get_redis_session_history(session_id: str, **kwargs):
    r = get_redis_connection()
    history = r.get(f"chat:{session_id}")
    return json.loads(history) if history else []


def append_to_session_history(session_id: str, user_input: str, assistant_response: str, expiration_time: int = 3600, **kwargs):
    r = get_redis_connection()
    history = get_redis_session_history(session_id)
    history.append({"user_input": user_input, "assistant_response": assistant_response})
    
    r.set(f"chat:{session_id}", json.dumps(history), ex=expiration_time)
