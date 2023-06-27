from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from typing import List

app = FastAPI()

# 정적 파일 (HTML, CSS, JS 등)을 제공하기 위해 StaticFiles를 설정합니다.
app.mount("/static", StaticFiles(directory="static"), name="static")

# 템플릿 엔진을 초기화합니다.
templates = Jinja2Templates(directory="templates")


class ChatMessage:
    def __init__(self, username: str, message: str):
        self.username = username
        self.message = message


class ChatRoom:
    def __init__(self):
        self.messages = []

    def add_message(self, message: ChatMessage):
        self.messages.append(message)

    def get_messages(self) -> List[ChatMessage]:
        return self.messages


chat_room = ChatRoom()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        username, message = message.split(":")
        chat_message = ChatMessage(username=username, message=message)
        chat_room.add_message(chat_message)
        await broadcast_message(chat_message)


async def broadcast_message(message: ChatMessage):
    for connection in app.state.connections:
        await connection.send_json(message.__dict__)


@app.on_event("startup")
async def startup_event():
    app.state.connections = set()


@app.on_event("shutdown")
async def shutdown_event():
    for connection in app.state.connections:
        await connection.close()


@app.middleware("http")
async def add_websocket_connections(request: Request, call_next):
    if request.url.path == "/ws":
        await call_next(request)
    else:
        response = await call_next(request)
        return response


@app.get("/")
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    app.state.connections.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"You wrote: {data}")
    except WebSocketDisconnect:
        app.state.connections.remove(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)

