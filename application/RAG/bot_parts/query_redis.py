import redis
import json

# Initialize Redis connection
def get_redis_connection():
    return redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

def get_redis_session_history(session_id: str, **kwargs):
    r = get_redis_connection()
    history = r.get(f"chat:{session_id}")
    return json.loads(history) if history else []

def append_to_session_history(session_id: str, user_input: str, assistant_response: str, expiration_time: int = 3600, **kwargs):
    r = get_redis_connection()
    history = get_redis_session_history(session_id)
    history.append({"user_input": user_input, "assistant_response": assistant_response})
    r.setex(f"chat:{session_id}", expiration_time, json.dumps(history))

# Example usage:
# append_to_session_history("123", "Hello", "Hi there!")
# print(get_session_history("123"))
