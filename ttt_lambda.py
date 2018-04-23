from slack_ttt.response_message import ResponseMessageBuilder as RMB
from slack_ttt import util
from urllib.parse import parse_qs
from slack_ttt import RequestHandler
from settings import (
                        KMS_ENCRYPTED_TOKEN,
                     )

def lambda_handler(event, context):
    resource = event["resource"]
    params = parse_qs(event['body'])
    token = params['token'][0]
    expected_token = util.decrypt(KMS_ENCRYPTED_TOKEN)
    if token != expected_token:
        return RMB.respond(err=Exception('Invalid request token'),
                           game_response_type='',
                           values=[])

    rh = RequestHandler(params)
    return rh.route(resource)