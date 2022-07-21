import json
import boto3
import string
import random
import time
import os
import sys, datetime
from botocore.vendored import requests
from botocore.config import Config

SSM_PARAM = os.environ.get("SSM_PARAMETER")
REGION = os.environ.get("REGION")
DB_NAME = os.environ.get("DB_NAME")
SLACK_URL = os.environ.get("SLACK_URL")
ENV = os.environ.get("ENV")

E_MESSAGE = ["PARAMETER STORE not updated correctly","Parameter Store value and New generated password doesn't match", "Error updating Master Password on RDS Instance "]
S_MESSAGE = "PARAMETER STORE UPDATE AND MASTER PASSWORD CHANGED"

DATE = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")


def lambda_handler(event, context):
    # Generate and Update Master Password
    new_password=generate_pass()
    update_parameter_store(new_password)
    reset_master_password(new_password)


def set_payload(status, message, date, env): 
    pay = {
    	"blocks": [
    		{
    			"type": "header",
    			"text": {
    				"type": "plain_text",
    				"text": "RDS MASTER PASSWORD UPDATED"
    				
    			}
    		},
    		{
    			"type": "section",
    			"fields": [
    				{
    					"type": "mrkdwn",
    					"text": "*STATUS:*\n" + status
    				},
    				{
    					"type": "mrkdwn",
    					"text": "*ENV*\n" + env
    				}
    			]
    		},
    		{
    			"type": "context",
    			"elements": [
    				{
    					"type": "plain_text",
    					"text": message
    				}
    			]
    		},
    		{
    			"type": "section",
    			"fields": [
    				{
    					"type": "mrkdwn",
    					"text": "*When:*\n" + date
    				}
    			]
    		}
    	]
    }
    payload = json.dumps(pay)
    return payload


def slack_notification(status, message): 
    region = 'us-west-1'
    
    # For TESTing SET SLACk_URL 
    SLACK_URL = "https://hooks.slack.com/services/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"

    url = "https://hooks.slack.com/services/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"

    # Update the payload information 
    
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
    response = requests.request('POST', SLACK_URL, data=set_payload(status, message, DATE, ENV), headers=headers)
    print(response.text)

def generate_pass():
    # Define length of password
    # Create random Password
    length = 24
    source = string.ascii_uppercase + string.ascii_lowercase + string.digits
    result_str = "".join((random.choice(source) for i in range(length)))
    return result_str

def get_current_param(): 
    ssm = boto3.client('ssm')

    current_param = ssm.get_parameter(Name=SSM_PARAM, WithDecryption=True)
    return current_param['Parameter']['Value']

def update_parameter_store(new_password):
    ssm = boto3.client('ssm')

    # Sets the new password in Parameter store
    try:
      
      ssm.put_parameter(Name=SSM_PARAM, Value=new_password, Overwrite=True, Type='SecureString')
      print("Parameter Store Value Updated" + SSM_PARAM)
      new_param = get_current_param()
    except:
      e = sys.exc_info()[0]
      print(e)
      STATUS = "FAILED"
      MESSAGE = E_MESSAGE[0] + " for" + SSM_PARAM
      slack_notification(STATUS, MESSAGE)
      sys.exit()
    
    print(new_param)
    print(new_password)
    if new_param != new_password: 
        STATUS = "FAILED"
        slack_notification(STATUS, E_MESSAGE[1])
        sys.exit()

def reset_master_password(new_password):
    NEW = new_password
    my_config = Config(
        region_name = REGION,
        signature_version = 'v4',
        retries = {
            'max_attempts': 10,
            'mode': 'standard'
        })
    #Sets the new master password on the RDS DB instance
    try:
        client = boto3.client('rds', config=my_config)
        response = client.modify_db_instance( DBInstanceIdentifier=DB_NAME, MasterUserPassword=NEW)
        print("Master Password Updated")
        
    except:
        print("Updating Master Password FAILED")
    
    if response != "": 
        STATUS = "SUCCESFULL"
        MESSAGE = S_MESSAGE
    else: 
        STATUS = "FAILED"
        MESSAGE = E_MESSAGE[2] + DB_NAME
    
    slack_notification(STATUS, MESSAGE)

    


