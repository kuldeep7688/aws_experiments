from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"message": "FastAPI is running on AWS Beanstalk"}


@app.post("/predict")
def predict(data: dict):
    # Dummy BERT classification logic
    return {"label": "positive", "confidence": 0.95}


@app.post("/openai-predict")
def openai_predict(data: dict):
    return {"classification": "negative", "confidence": 0.70}
