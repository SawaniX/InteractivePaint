from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from WebSocket.connection_manager import ConnectionManager

app = FastAPI()

origins = [
    'http://localhost'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


manager = ConnectionManager()

@app.get('/')
async def root():
    return {'Wiadomość': ""}


@app.websocket('/virtual_paint')
async def virtual_paint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_bytes()
            await manager.send_personal_message(f'Message: {data}')
    except WebSocketDisconnect:
        manager.disconnect(websocket)
