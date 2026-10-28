from fastapi import FastAPI

from controllers import router


app = FastAPI()
app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "ok"}