
from fakeredis.aioredis import FakeRedis
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from push.adapter.websocket_connection_manager import \
    RedisWebSocketConnectionManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def redis_conn():
    return FakeRedis()

def websocket_connection_manager(redis_conn=Depends(redis_conn)):
    return RedisWebSocketConnectionManager(redis_conn)
