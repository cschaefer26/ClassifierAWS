import os
import uvicorn
import boto3
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from classifier.model import TextClassifier
import logging


def download_classifier():
    model_bucket_name = os.environ['MODEL_BUCKET_NAME']
    s3_client = boto3.client('s3')
    with open('classifier.pkl', 'wb') as f:
        s3_client.download_fileobj(model_bucket_name, 'classifier.pkl', f)
    classifier = TextClassifier.load('classifier.pkl')
    return classifier


classifier = download_classifier()
app = FastAPI()
templates = Jinja2Templates(directory="templates/")


@app.get('/')
def read_form():
    return 'hello world'


@app.get("/classify")
def form_post(request: Request):
    classifier_result = {}
    return templates.TemplateResponse('form_template.html', context={'request': request, 'classifier_result': classifier_result})


@app.post("/classify")
def form_post(request: Request, text: str = Form(...)):
    classifier_result = classifier(text)
    return templates.TemplateResponse('form_template.html', context={'request': request, 'classifier_result': classifier_result})


if __name__ == "__main__":
    logging.basicConfig(format='{levelname:7} {message}', style='{', level=logging.INFO)
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    uvicorn.run(app, host="0.0.0.0", port=80, debug=True, log_config=None)

