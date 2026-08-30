# Hello World Service

Foundation ফেজের CI/CD পাইপলাইন যাচাই করার জন্য একটা dummy stateless সার্ভিস।

## লোকালি রান করার নিয়ম

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

তারপর ব্রাউজারে যান: http://127.0.0.1:8000/healthz

## Docker দিয়ে রান করার নিয়ম

```bash
docker build -t hello-world .
docker run -p 8000:8000 hello-world
```