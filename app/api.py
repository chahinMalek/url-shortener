from importlib.metadata import version

from fastapi import FastAPI

app = FastAPI(
    title="URL Shortener",
    description="Simple URL shortener service",
    version=version("url-shortener"),
)


@app.get("/")
async def root():
    return {"message": "URL Shortener API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
