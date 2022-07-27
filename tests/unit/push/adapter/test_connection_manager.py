import logging
from asyncio import sleep

from fakeredis.aioredis import FakeRedis
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket

from push.adapter.websocket_connection_manager import \
    RedisWebSocketConnectionManager

logger = logging.getLogger(__name__)

async def test_basic_scenario():
    app = FastAPI()
    conn = FakeRedis()
    manager = RedisWebSocketConnectionManager(conn)

    @app.websocket('/ws/{user_id}')
    async def websocket_endpoint(ws: WebSocket, user_id:str):
        await ws.accept()
        await manager.connect(user_id=user_id, ws=ws)
        await ws.close()

    client = TestClient(app)
    with client.websocket_connect('/ws/1') as websocket_client_1_1, \
            client.websocket_connect('/ws/1') as websocket_client_1_2, \
            client.websocket_connect('/ws/2') as websocket_client_2:
        await sleep(0.1)
        test_data_1 = {'event_name': 'test_data', 'payload': 'hello'}
        test_data_2 = {'event_name': 'test_data2'}
        await manager.send_push_message(user_id=1, data=test_data_1)
        await manager.send_push_message(user_id=2, data=test_data_2)
        received_data_1_1 = websocket_client_1_1.receive_json()
        received_data_1_2 = websocket_client_1_2.receive_json()
        received_data_2 = websocket_client_2.receive_json()
        websocket_client_1_1.close()
        websocket_client_1_2.close()
        websocket_client_2.close()
    assert received_data_1_1 == test_data_1
    assert received_data_1_2 == test_data_1
    assert received_data_2 == test_data_2
