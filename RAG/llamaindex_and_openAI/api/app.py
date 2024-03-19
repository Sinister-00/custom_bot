from flask import Flask, request, jsonify
import os.path
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage
)
import boto3
import pandas as pd
import json
import os
from dotenv import load_dotenv
import requests

load_dotenv()

S3_REGION = os.getenv('S3_BUCKET_REGION')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

PERSIST_DIR = "./storage"
index = None
signed_url=None

# Initialize Flask app
app = Flask(__name__)

def download_s3_folder(bucket_name, s3_folder, local_folder):
    s3 = boto3.resource('s3',    region_name=S3_REGION,
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'))
    bucket = s3.Bucket(bucket_name)

    for obj in bucket.objects.filter(Prefix=s3_folder):
        target = os.path.join(local_folder, os.path.relpath(obj.key, s3_folder))
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        bucket.download_file(obj.key, target)
        print(f'Downloaded s3://{bucket_name}/{obj.key} to {target}')

def download_s3_folder_with_signed_url(bucket_name, s3_folder, local_folder):
    s3 = boto3.client('s3',    region_name=S3_REGION,
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'))
    response=s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_folder)
    for obj in response.get('Contents', []):
        target = os.path.join(local_folder, os.path.relpath(obj['Key'], s3_folder))
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': obj['Key']},ExpiresIn=20)
        print("URL: ",url)
        print(f'Downloading {url} to {target}')
        r = requests.get(url)
        with open(target, 'wb') as f:
            f.write(r.content)

def initialize_index():
    global index
    if not os.path.exists(PERSIST_DIR):
        download_s3_folder_with_signed_url(S3_BUCKET_NAME, "storage", "storage")
        print("Created and stored index")
    else:
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
        print("Loaded index from storage")
    return index


def convert_to_serializable(response):
    if isinstance(response, str):
        return response
    elif isinstance(response, list):
        return [convert_to_serializable(item) for item in response]
    elif isinstance(response, dict):
        return {key: convert_to_serializable(value) for key, value in response.items()}
    elif hasattr(response, '__dict__'):
        return convert_to_serializable(response.__dict__)
    else:
        return str(response)



@app.route('/load_storage', methods=['GET'])
def load_storage():
    global index
    index = initialize_index()
    print("Index loaded",index)
    return jsonify({'status': 'success'})


@app.route('/query_rag', methods=['POST'])
def query_rag():
    global index
    print(index)
    data = request.get_json()
    query_text = data.get('query')

    if not query_text:
        return jsonify({'error': 'Query not provided'}), 400

    query_engine = index.as_query_engine()
    response = query_engine.query(query_text)

    serializable_response = convert_to_serializable(response)

    return jsonify({'response': serializable_response["response"]})



@app.route('/query_openai', methods=['POST'])
def query_openai():
    data = request.get_json()
    query_text = data.get('query')
    print(query_text)


if __name__ == '__main__':
    app.run(debug=True)