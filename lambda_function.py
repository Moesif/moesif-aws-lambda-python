from moesif_aws_lambda.middleware import *
import os
import requests
import json

moesif_options = {
    'LOG_BODY': True,
    'DEBUG': True,
}

@MoesifLogger(moesif_options)
def lambda_handler(event, context):

    # Outgoing API call to third parties like Github / Stripe or to your own dependencies
    start_capture_outgoing(moesif_options)
    third_party = requests.get('https://httpbin.org/ip', json=json.dumps({'test': 2}),
                               headers={"content-type": "text", "Authorization": "Bearer sdf4854wer"},
                               auth=('Basic', "testauth"))

    return {
        'statusCode': 200,
        'isBase64Encoded': False,
        'body': {
            'msg': 'Hello from Lambda!'
            },
        'headers': {
            'Content-Type': 'application/json'
            }
    }
