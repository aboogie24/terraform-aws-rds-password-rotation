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
    except:
        print("Error updating Master Password")
