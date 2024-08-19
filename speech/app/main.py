from fastapi import FastAPI
# from app.api.endpoints import router as api_router
from speech.app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the Speech API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)