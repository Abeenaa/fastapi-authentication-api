import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

_lock = threading.Lock()
_hits: dict[str, deque[float]] = defaultdict(deque)


def rate_limiter(limit: int, window_seconds: int, bucket: str):
    def dependency(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"{bucket}:{client_ip}"
        now = time.time()

        with _lock:
            history = _hits[key]
            cutoff = now - window_seconds
            while history and history[0] <= cutoff:
                history.popleft()

            if len(history) >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded for {bucket}. Try again later.",
                )

            history.append(now)

    return dependency
