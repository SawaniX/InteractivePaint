from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from WebSocket.connection_manager import ConnectionManager
from ImageProcessing.image_processing import ImageProcessing

app = FastAPI()
recognizer = ImageProcessing()

origins = [
    'http://localhost:3000', 'http://192.168.0.178:3000'
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
            data = await websocket.receive_text()
            if len(data) > 10:
                processed_image = recognizer.process_image(data)
                await manager.send_personal_message(processed_image, websocket)
            else:
                await manager.send_personal_message("Processing image failed", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get('/fill_sketch', 
          responses={200: {'content': {'image/png': {}}}}, 
          response_class=Response)
async def fill_sketch():
    inpainted = recognizer.inpaint_sketch('dogs')
    return JSONResponse(content={'inpainted': inpainted})


@app.post('/change_color')
async def change_color(color: str):
    recognizer.set_color(color)
    return Response()


@app.post('/change_thickness')
async def change_thickness(thickness: int):
    recognizer.set_thickness(thickness)
    return Response()
