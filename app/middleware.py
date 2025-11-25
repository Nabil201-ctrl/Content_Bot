import time
import logging
from fastapi import Request

logger = logging.getLogger("uvicorn.access")


async def request_time_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    response.headers["X-Process-Time"] = str(elapsed)
    logger.info(f"{request.method} {request.url.path} completed_in={elapsed:.3f}s")
    return response


from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class SimpleAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method != "GET":
            api_key = request.headers.get("x-api-key")
            if api_key != "expected-secret":
                return JSONResponse({"detail": "Unauthorized"}, status_code=401)
        return await call_next(request)
# Import the time module to measure the time taken to process a request.
import time
# Import the logging module to log information about requests.
import logging
# Import the Request class from FastAPI to represent an HTTP request.
from fastapi import Request

# Get the logger instance for "uvicorn.access" to log access-related messages.
logger = logging.getLogger("uvicorn.access")

# Asynchronous middleware function to measure the processing time of a request.
async def request_time_middleware(request: Request, call_next):
    # Record the start time of the request processing.
    start = time.time()
    # Call the next middleware or the request handler to get the response.
    response = await call_next(request)
    # Calculate the elapsed time for the request.
    elapsed = time.time() - start
    # Add a custom header to the response with the processing time.
    response.headers["X-Process-Time"] = str(elapsed)
    # Log the request method, URL path, and processing time.
    logger.info(f"{request.method} {request.url.path} completed_in={elapsed:.3f}s")
    # Return the response.
    return response

# Example simple auth middleware (placeholder). For production, use dependencies or proper auth libs.
# Import JSONResponse to create a JSON response for unauthorized access.
from fastapi.responses import JSONResponse
# Import BaseHTTPMiddleware from Starlette to create a custom middleware class.
from starlette.middleware.base import BaseHTTPMiddleware

# A simple authentication middleware class that checks for an API key in the request headers.
class SimpleAuthMiddleware(BaseHTTPMiddleware):
    # The dispatch method is called for each request.
    async def dispatch(self, request: Request, call_next):
        # Example: require an API key header for non-GET routes
        # Check if the request method is not GET.
        if request.method != "GET":
            # Get the API key from the request headers.
            api_key = request.headers.get("x-api-key")
            # Check if the API key is not the expected secret key.
            if api_key != "expected-secret":
                # Return a JSON response with an "Unauthorized" detail and a 401 status code.
                return JSONResponse({"detail": "Unauthorized"}, status_code=401)
        # If the authentication is successful or not required, call the next middleware or request handler.
        return await call_next(request)
