import json
import boto3
import string
import random
import time
import os
import sys
from botocore.vendored import requests
from botocore.config import Config

SSM_PARAM = os.environ.get("SSM_PARAMETER")
REGION = os.environ.get("REGION")
DB_NAME = os.environ.get("DB_NAME")


def lambda_handler(event, context):
    # Generate and Update Master Password
    new_password=generate_pass()
    update_parameter_store(new_password)
    reset_master_password(new_password)

def slack_notification(): 
    region = 'us-west-1'


    url = "https://hooks.slack.com/services/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"
    
    # Update the payload information 
    payload = '{ \"attachments\":[\n      {\n         \"fallback\":\"Jenkins: <http://localhost:8080/|Open Jenkins Build server here>\",\n         \"pretext\":\"Jenkins: <http://localhost:8080/|Open Jenkins Build server here>\",\n         \"color\":\"#34bb13\",\n         \"fields\":[\n            {\n               \"title\":\"Password Reset\",\n               \"value\":\"Parmeter Store Password has been reset\"\n            }\n         ]\n      }\n   ]\n }'
    headers = {
        'Content-Type': "application/json",
        'User-Agent': "PostmanRuntime/7.19.0",
        'Accept': "*/*",
        'Cache-Control': "no-cache",
        'Postman-Token': "56df98df-XXXX-XXXX-XXXX-9a2k5q56b8gf,458sadwa-XXXX-XXXX-XXXX-p456z4564a45",
        'Host': "hooks.slack.com",
        'Accept-Encoding': "gzip, deflate",
        'Content-Length': "497",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
        }
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)

def generate_pass():
    # Define length of password
    # Create random Password
    length = 24
    source = string.ascii_uppercase + string.ascii_lowercase + string.digits
    result_str = "".join((random.choice(source) for i in range(length)))
    return result_str

def update_parameter_store(new_password):
    ssm = boto3.client('ssm')

    # Gets the current password set in parameter store
    # Make sure to variablize the path string
    parameter = ssm.get_parameter(Name=SSM_PARAM, WithDecryption=True)

    # Sets the new password in Parameter store
    try:
      ssm.put_parameter(Name=SSM_PARAM, Value=new_password, Overwrite=True, Type='SecureString')
      print("New Parameter Store Value: " + new_password)
      
    except:
      e = sys.exc_info()[0]
      print(e)
      sys.exit()
      

    # Ensure the password has been set in parameter store by pulling the new password
    parameter = ssm.get_parameter(Name=SSM_PARAM, WithDecryption=True)

def reset_master_password(new_password):
    NEW = new_password
    my_config = Config(
        region_name = REGION,
        signature_version = 'v4',
        retries = {
            'max_attempts': 10,
            'mode': 'standard'
        })

    client = boto3.client('rds', config=my_config)

    #Sets the new master password on the RDS DB instance
    try:
        response = client.modify_db_instance( DBInstanceIdentifier=DB_NAME, MasterUserPassword=NEW)
        print("Master Password Updated")
        print("   value: " + NEW)
        slack_notification()
    except:
        print("Error updating Master Password")
