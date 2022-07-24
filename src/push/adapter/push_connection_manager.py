import asyncio
import json
import logging
from datetime import date, datetime

from fastapi import WebSocketDisconnect
from fastapi.websockets import WebSocket
from redis.asyncio import Redis
from redis.asyncio.client import PubSub

logger = logging.getLogger(__name__)
CHANNEL_KEY_PREFIX='push-service:RedisPushConnectionManager'

def generate_channel(user_id):
        return f'{CHANNEL_KEY_PREFIX}:{user_id}'

async def send_push_message_handler(pubsub:PubSub, ws: WebSocket):
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
            if message:
                data = message.get('data')
                await ws.send_text(data)
    except Exception as e:
        logger.exception(e)

# It is used for catching WebSocketDisconnect exception
async def websocket_receiver_handler(ws: WebSocket):
    logger.info(f'websocket_receiver_handler()')
    try:
        while True:
            _ = await ws.receive_text()
    except WebSocketDisconnect as e:
        logger.exception(e)

class RedisPushConnectionManager:
    def __init__(self, conn: Redis):
        self.conn = conn

    async def connect(self, user_id: int, ws:WebSocket):
        logger.info(f'connect(user_id={user_id})')
        
        pubsub = self.conn.pubsub()
        push_channel = generate_channel(user_id)
        logger.info(f'subscribe(push_channel={push_channel})')
        
        await pubsub.subscribe(push_channel)
        try:
            await self.__run_handler(pubsub, ws)
        finally:
            await pubsub.unsubscribe(push_channel)

        logger.info(f'finish tasks in connect(user_id={user_id})')

    async def send_push_message(self, user_id:int, data:dict):
        logger.info(f'send_push_message(user_id={user_id}, data={data})')
        def serialize(value):
            if isinstance(value, datetime) or isinstance(value, date):
                return value.isoformat()
            return value
        push_channel = generate_channel(user_id)
        serialized_data = json.dumps({key:serialize(value) for key, value in data.items()})
        await self.conn.publish(push_channel, serialized_data)

    async def __run_handler(self, pubsub:PubSub, ws:WebSocket):
        push_message_task = asyncio.create_task(send_push_message_handler(pubsub, ws))
        receiver_task = asyncio.create_task(websocket_receiver_handler(ws))
        _, pending = await asyncio.wait(
            [receiver_task, push_message_task], return_when=asyncio.FIRST_COMPLETED)
        
        for task in pending:
            logger.debug(f'Canceling task: {task}')
            task.cancel()
