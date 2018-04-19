import boto3
import json
from base64 import b64decode
from urllib.parse import parse_qs
from slack_ttt import req_handler as rh
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
        return rh.respond(Exception('Invalid request token'))

    custom_text = None
    if 'text' in params:
        custom_text = params['text'][0]

    response = None

    # Simple router
    if resource == '/ttt':
        response = rh.new_game(custom_text)
    elif resource == '/ttt-help':
        response = rh.game_help()
    elif resource == '/ttt-accept':
        response = rh.accept()
    elif resource == '/ttt-decline':
        response = rh.decline()
    elif resource == '/ttt-board':
        response = rh.board()
    elif resource == '/ttt-move':
        response = rh.move(custom_text)
    elif resource == 'ttt-end':
        response = rh.end()
    else:
        response = rh.invalid_request()

    return response
