from fastapi import FastAPI

app = FastAPI(title="Hello World Service")

@app.get("/")
def root():
    return {"message": "AI Assistant Platform - Foundation service is running"}

@app.get("/healthz")
def healthz():
    """লাইভনেস চেক - সার্ভিস চালু আছে কিনা"""
    return {"status": "ok"}

@app.get("/readyz")
def readyz():
    """রেডিনেস চেক - সার্ভিস রিকোয়েস্ট নিতে প্রস্তুত কিনা"""
    return {"status": "ready"}