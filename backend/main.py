from fastapi import FastAPI

app = FastAPI(title="JobAutoApplier")


@app.get("/")
def home():
    return {
        "message": "JobAutoApplier API is running",
        "status": "success"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}