from moesif_aws_lambda.middleware import MoesifLogger
import os

moesif_options = {
    'LOG_BODY': True,
    'DEBUG': True,
}

@MoesifLogger(moesif_options)
def lambda_handler(event, context):
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
