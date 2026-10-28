from fastapi import FastAPI

from controllers import router, user_router


app = FastAPI()
app.include_router(router)
app.include_router(user_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}