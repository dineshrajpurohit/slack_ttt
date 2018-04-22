import boto3
import json
from base64 import b64decode
from urllib.parse import parse_qs
from slack_ttt import RequestHandler
from settings import (
                        KMS_ENCRYPTED_TOKEN,
                     )

kms = boto3.client('kms')
expected_token = kms.decrypt(CiphertextBlob=b64decode(KMS_ENCRYPTED_TOKEN))['Plaintext']


def lambda_handler(event, context):
    resource = event["resource"]
    params = parse_qs(event['body'])
    token = params['token'][0]
    if token != expected_token.decode():
        return RequestHandler.respond(Exception('Invalid request token'))

    rh = RequestHandler(params)
    return rh.route(resource)