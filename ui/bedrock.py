import boto3
import json
import os
from database import add_log

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

def stream_response(prompt, max_tokens):
    body = json.dumps({
        'prompt': prompt,
        'max_tokens': max_tokens,
    })
       
    response = bedrock_runtime.invoke_model_with_response_stream(
        modelId='mistral.mistral-7b-instruct-v0:2', 
        body=body
    )
    
    stream = response.get('body')
    response = ''
    if stream:
        for event in stream:
            chunk = event.get('chunk')
            if chunk:
                token = json.loads(chunk.get('bytes').decode())['outputs'][0]['text']
                response += token
                yield token
    add_log(prompt, response)
