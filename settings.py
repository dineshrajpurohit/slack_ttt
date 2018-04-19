"""
AWS Lambda settings for Slack Tic-Tac-Toe project.

"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuration for choosing Salesforce or Python as app logic default: salesforce
LOGIC_SOURCE = "salesforce"

# Salesforce related configuation (If SFDC is the main logic source)
SFDC_USERNAME = os.environ["SFDC_USERNAME"]
SFDC_PASSWORD = os.environ["SFDC_PPASSWORD"]
SFDC_TOKEN    = os.environ["SFDC_TOKEN"]

# Encrypment token for AWS KMS
KMS_ENCRYPTED_TOKEN = os.environ['kmsEncryptedToken']
