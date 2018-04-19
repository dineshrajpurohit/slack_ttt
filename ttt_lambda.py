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

    # Simple router
    if resource == '/ttt':
        print(event.method)
        rh.new_game()
    elif resource == '/ttt-help':
        rh.game_help()
    elif resource == '/ttt-accept':
        rh.accept()
    elif resource == '/ttt-decline':
        rh.decline()
    elif resource == '/ttt-board':
        rh.board()
    elif resource == '/ttt-move':
        rh.move()
    elif resource == 'ttt-end':
        rh.end()
    else:
        print
        "Invalid call"
