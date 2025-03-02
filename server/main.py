import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from views import chat, root


def add_static_files(app: FastAPI):
    app.mount("/static", StaticFiles(directory="static"), name="static")


# function for enabling CORS on web server
def add_cors(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"])


app = FastAPI()

add_cors(app)
add_static_files(app)

app.include_router(chat.router)
app.include_router(root.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
