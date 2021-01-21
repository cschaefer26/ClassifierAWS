import time
import os
import boto3
from flask import Flask, request, jsonify, render_template
import json
import os
import time
import boto3
from botocore.client import BaseClient
import logging
import logging.config
import yaml
from classifier.model import TextClassifier


app = Flask(__name__)


@app.route('/classify')
def my_form():
    return render_template('form_template.html', classifier_result={})


@app.route('/classify', methods=['POST'])
def my_form_post():
    text = request.form['text']
    app.logger.info(f'Processing classification request with text: {text}')
    result = classifier(text)
    #result = jsonify(result)
    #classes = sorted(list(result.keys()), key=result.get, reverse=True)
    #result_string = ''.join([f'{c}: {result[c]}\n' for c in classes])
    return render_template('form_template.html', classifier_result=result)


"""
@app.route('/classify', methods=['GET'])
def classify():
    string = request.args.get('text')
    app.logger.info(f'Processing classification request with string: {string}')
    result = classifier(string)
    result = jsonify(result)
    return result
"""

@app.route('/', methods=['GET'])
def health():
    return 'healthy.'



if __name__ == '__main__':
    model_bucket_name = os.environ['MODEL_BUCKET_NAME']
    region = os.environ['AWS_REGION']
    s3_client = boto3.client('s3')

    with open('logging-config.yaml', 'r') as f:
        log_cfg = yaml.safe_load(f.read())
    logging.config.dictConfig(log_cfg)

    logger = logging.getLogger(__name__)
    logger.info(f'Downloading model from bucket: {model_bucket_name}')
    with open('classifier.pkl', 'wb') as f:
        s3_client.download_fileobj(model_bucket_name, 'classifier.pkl', f)
    classifier = TextClassifier.load('classifier.pkl')

    port = 80
    logger.info(f'Running flask app on port {port}!')
    app.run(host="0.0.0.0", port=port)

