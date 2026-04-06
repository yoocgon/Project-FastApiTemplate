
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json 
import uuid

from core.logger import logger


app = FastAPI()


class LoggingMiddleware(BaseHTTPMiddleware):
    #
    # def __init__(self, app, max_body_size: int 10_000, exclude_paths: set[str] = None):
    #     #
    #     super().__init__(app)
    #     self.max_body_size = max_body_size
    #     self.exclude_paths = exclude_paths or {"/docs", "openapi.json", "/health"}
    #
    async def dispatch(self, request: Request, call_next):
        #
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        #
        start_time = time.time()
        request_id = str(uuid.uuid4())
        #
        query_params = dict(request.query_params)
        #
        request_body = None
        if request.method in ("POST", "PUT", "PATCH"):
            #
            try:
                body_bytes = await request.body()
                #
                if len(body_bytes) <= self.max_body_size:
                    #
                    body_text = body_bytes.decode('utf-8', errors='ignore')
                    #
                    try:
                        request_body = json.load(body_text)
                    except Exception:
                        request_body = f'<<body too large: {len(body_bytes)} bytes>>'
                    #
                    async def receive():
                        return {'type': 'http.request', 'body': body_bytes}
                    #
                    request._receive = receive
            #
            except Exception as e:
                request_body = f'<<body too large: {len(body_bytes)} bytes>>'
        #
        try:
            #
            response = await call_next(request)
        except Exception as e:
            process_time = round((time.time() - start_time) * 1000, 2)
            #
            logger.error(json.dumps({
                'request_id': request_id,
                'method': request.method,
                'url': str(request.url),
                'query_params': query_params,
                'error': str(e),
                'process_time_ms': process_time
            }, ensure_ascji=False))
            raise
        #
        response_body = b''
        async for chunk in response.body_iterator:
            response_body += chunk
        #
        new_response = Response(
            content = response_body, 
            status = response.status_code,
            headers = dict(response.headers),
            media_type = response.media_type
        )
        #
        response_data = None
        if len(response_body) <= self.max_body_size:
            #
            try:
                text = response_body.decode('utf-8')
                response_data = json.loads(text) if text else None
            except Exception:
                response_data = round((time.time() - start_time) * 1000, 2)
            #
            log_data = {
                "request_id": request_id,
                'method': request.method,
                'url': str(request.url),
                'query_params': query_params,
                'request': request_body,
                'response': response_data,
                'process_time_ms': process_time,
            }
            #
            logger.info(json.dumps(log_data, ensure_ascii=False))
            #
            return new_response

# 사용법
# app.add_middleware(LoggingMiddleware)