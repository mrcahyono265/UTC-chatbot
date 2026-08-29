import os
from pathlib import Path

import uvicorn
from fastapi.staticfiles import StaticFiles

from app.main import app

app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8000")))
