
import json
import time
import uvicorn

from datetime import datetime
from fastapi import FastAPI, Request, Response, status, Depends
from fastapi.exceptions import RequestValidationError
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from functools import lru_cache
from starlette.responses import Response, StreamingResponse, JSONResponse
from sqlmodel import Field, SQLModel
from starlette.exceptions import HTTPException

import core.auth as auth
import core.oracle as oracle_db
import core.sqlite as sqlite_db
import core.setting as settings
import core.logger as logger

from core.oracle import get_engine as get_oracle_engine
from core.sqlite import get_engine as get_sqlite_engine
from core.logger import log_dict, log_response
from exception.custom import NotFoundException, AlreadyExistsException, AppException
from exception.handlers import app_exception_handler
from models.settings import Settings
from response import CommonResponse
from routers.hero import router as hero_router
from routers.login import router as login_router
from routers.user import router as user_router
from services.login import LoginService
from models.token import TokenORM, Token
from models.user import UserORM, User
from models.hero import HeroORM, Hero


settings.init()    
logger.init()
auth.init()
oracle_db.init()
sqlite_db.init()
# server.init()
app = FastAPI()


@app.on_event("startup")
def on_startup():
    #
    oracle_tables = [
        UserORM.__table__, 
        HeroORM.__table__,    
    ]
    SQLModel.metadata.create_all(get_oracle_engine(), tables=oracle_tables)
    #
    sqlite_tables = [
        TokenORM.__table__, 
    ]
    SQLModel.metadata.create_all(get_sqlite_engine(), tables=sqlite_tables)
    #
    FastAPICache.init(InMemoryBackend())


@lru_cache
def get_settings():
    return Settings()


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    #
    respones = JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": "An error occurred with the request",
            "detail": exc.detail
        },
        headers=exc.headers
    )
    #
    log_response(respones, 'ERROR')
    #
    return respones


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    #
    status_code=str(type(exc).__name__)
    detail = str(exc.args) 
    #
    response = JSONResponse(
        status_code=500,
        content={
            "code": status_code,
            "message": "Internal Server Error",
            "details": detail 
        },
    )
    #
    log_response(response, 'ERROR')
    #
    return response


@app.middleware("http")
async def web_filter(request: Request, call_next):
    #
    str_start_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    str_url = str(request.url)
    str_method = request.method
    str_request_content_type = request.headers.get("content-type")
    str_qyery_parameters = dict(request.query_params)
    str_request_header = dict(request.headers)
    str_request_body = {}
    str_response_media_type = ''
    str_response_header = {}
    str_response_body = {}
    str_response_text = ''
    str_status_code = ''
    str_exception_type = ''
    str_exception_message = ''
    str_finish_timestamp = ''
    str_processing_time = ''
    #
    response_body = b''
    #
    request_body = None
    request_body = await request.body()
    if request_body != b'':
        request_body_str = request_body.decode('utf-8')
        str_request_body = json.loads(request_body_str)
    #
    str_dict = {
        'str_type': 'http',
        'start_timestamp': str_start_timestamp,
        'url': str_url,
        'method': str_method,
        'request_media_type': str_request_content_type,
        'qyery_parameters': str_qyery_parameters,
        'request_header': str_request_header,
        'request_body': str_request_body,
        'response_media_type': str_response_media_type,
        'response_header': str_response_header,
        'response_body': str_response_body,
        'response_text': str_response_text,
        'status_code': str_status_code,
        'exception_message': str_exception_message,
        'exception_type': str_exception_type,
        'finish_timestamp': str_finish_timestamp,
        'processing_time': str_processing_time
    }
    #
    log_dict(str_dict, level='INFO')
    #
    start_time = time.perf_counter()
    response = None
    response = await call_next(request)
    str_processing_time = time.perf_counter() - start_time
    #
    if response:
        #
        response.headers["X-Process-Time"] = str(str_processing_time)
        #
        headers=dict(response.headers)
        str_response_header = headers
        str_status_code = response.status_code
        #
        if not isinstance(response, StreamingResponse):
            async for chunk in response.body_iterator:
                response_body += chunk
            #
            response_body_str = response_body.decode('utf-8')
            if 'text/html' not in headers['content-type']:
                str_response_body = json.loads(response_body_str)
    #
    str_finish_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #
    str_dict = {
        'str_type': 'http',
        'start_timestamp': str_start_timestamp,
        'url': str_url,
        'method': str_method,
        'request_media_type': str_request_content_type,
        'qyery_parameters': str_qyery_parameters,
        'request_header': str_request_header,
        'request_body': str_request_body,
        'response_media_type': str_response_media_type,
        'response_header': str_response_header,
        'response_body': str_response_body,
        'response_text': str_response_text,
        'status_code': str_status_code,
        'exception_message': str_exception_message,
        'exception_type': str_exception_type,
        'finish_timestamp': str_finish_timestamp,
        'processing_time': str_processing_time
    }
    #
    log_dict(str_dict, level='INFO')
    #
    if str_status_code != 200:
        raise Exception
    #
    if response_body == b'':
        response = response
    else:
        response = Response(
            content=response_body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type
        )
    #
    return response


@app.get("/")
async def main():
    #
    return {"message": "Hello World"}


@app.get("/mirae-asset/authorization/oauth2", response_model=Token)
async def auth(user: User, service: LoginService = Depends()):
    #
    if(service.verify_passwrod(user)):
        token = await service.isseue_token(user)
        return token
    #
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed Authorization!")


app.include_router(login_router)
app.include_router(user_router)
app.include_router(hero_router)

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(AppException, app_exception_handler)

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000, access_log=False, log_config=None)
