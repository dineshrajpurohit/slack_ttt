"""
Utility Class

"""
import boto3
from base64 import b64encode, b64decode

def encrypt(value):
    kms = boto3.client('kms')
    expected_token = kms.encrypt(CiphertextBlob=b64encode(value))['CiphertextBlob']
    return expected_token

def decrypt(token):
    kms = boto3.client('kms')
    expected_token = kms.decrypt(CiphertextBlob=b64decode(token))['Plaintext']
    return expected_token.decode()