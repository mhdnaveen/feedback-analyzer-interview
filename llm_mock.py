import time
from collections import deque
from fastapi import HTTPException

# Track request timestamps for each user
user_request_log = {}

def mock_llm_call(user_id: str, prompt: str):
    """
    Mock LLM call that raises a 429 error if the user exceeds
    78 requests within a 60-second rolling window.
    """
    now = time.time()
    window_seconds = 60
    max_requests = 78

    # Initialize log for new users
    if user_id not in user_request_log:
        user_request_log[user_id] = deque()

    requests_log = user_request_log[user_id]

    # Remove timestamps older than 60 seconds
    while requests_log and requests_log[0] < now - window_seconds:
        requests_log.popleft()

    # Check rate limit
    if len(requests_log) >= max_requests:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: max {max_requests} calls per {window_seconds}s"
        )

    # Log the new request timestamp
    requests_log.append(now)

    # Mocked LLM response
    return {
        "user_id": user_id,
        "input": prompt,
        "response": f"Mocked response for: '{prompt}'",
        "timestamp": now
    }


# Example usage:
if __name__ == "__main__":
    user = "user_123"
    for i in range(50):  # Simulate 80 calls quickly
        try:
            result = mock_llm_call(user, f"Message {i+1}")
            print(result["response"])
        except HTTPException as e:
            print(f"Error {e.status_code}: {e.detail}")
            break
