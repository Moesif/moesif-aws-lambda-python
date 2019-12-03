# Moesif AWS Lambda Middleware

[![Built For][ico-built-for]][link-built-for]
[![Software License][ico-license]][link-license]
[![Source Code][ico-source]][link-source]

Middleware (Python) to automatically log API calls from AWS Lambda functions
and sends to [Moesif](https://www.moesif.com) for API analytics and log analysis. 

Designed for APIs that are hosted on AWS Lambda using Amazon API Gateway as a trigger.

This middleware expects the
[Lambda proxy integration type.](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-set-up-simple-proxy.html#api-gateway-set-up-lambda-proxy-integration-on-proxy-resource)
If you're using AWS Lambda with API Gateway, you are most likely using the proxy integration type.

## How to install

```shell
pip install moesif_aws_lambda
```

## How to use

The following shows how import the module and use:

### 1. Import the module:

```python
from moesif_aws_lambda.middleware import MoesifLogger
import os

# Moesif Application Id
os.environ["MOESIF_APPLICATION_ID"] = "Your Moesif Application Id"

def identify_user(event, context):
    return 'my_user_id'

def identify_company(event, context):
    return 'my_company_id'

def get_api_version(event, context):
    return '1.0.0'

def get_session_token(event, context):
    return '23jdf0owekfmcn4u3qypxg09w4d8ayrcdx8nu2ng]s98y18cx98q3yhwmnhcfx43f'

def get_metadata(event, context):
    return { 'foo' : 'aws lambda', 'bar' : 'aws lambda metadata', }

def mask_event(eventmodel):
    return eventmodel

def should_skip(event, context):
    return "/" in event['path']

moesif_options = {
    'GET_METADATA': get_metadata,
    'IDENTIFY_USER': identify_user,
    'IDENTIFY_COMPANY': identify_company,
    'GET_SESSION_TOKEN': get_session_token,
    'GET_API_VERSION': get_api_version,
    'MASK_EVENT_MODEL': mask_event,
    'SKIP': should_skip,
    'LOG_BODY': True,
    'DEBUG': True
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
```

### 2. Enter Moesif Application Id
Your Moesif Application Id can be found in the [_Moesif Portal_](https://www.moesif.com/).
After signing up for a Moesif account, your Moesif Application Id will be displayed during the onboarding steps. 

You can always find your Moesif Application Id at any time by logging 
into the [_Moesif Portal_](https://www.moesif.com/), click on the top right menu,
 and then clicking _Installation_.

## Repo file structure

- `moesif_aws_lambda/middleware.py` the middleware library
- `lambda_function.py` sample AWS Lambda function using the middleware

## Configuration options

#### __`IDENTIFY_USER`__

Type: `(event, context) => String`

`IDENTIFY_USER` is a function that takes AWS lambda `event` and `context` objects as arguments
and returns a user_id. This enables Moesif to attribute API requests to individual unique users
so you can understand who calling your API. This can be used simultaneously with `IDENTIFY_COMPANY`
to track both individual customers and the companies their a part of.


```python
def identify_user(event, context):
  # your code here, must return a string
  return event["requestContext"]["identity"]["cognitoIdentityId"]
```

#### __`IDENTIFY_COMPANY`__

Type: `(event, context) => String`

`IDENTIFY_COMPANY` is a function that takes AWS lambda `event` and `context` objects as arguments
and returns a company_id. If your business is B2B, this enables Moesif to attribute 
API requests to specific companies or organizations so you can understand which accounts are 
calling your API. This can be used simultaneously with `IDENTIFY_USER` to track both 
individual customers and the companies their a part of. 


```python
def identify_company(event, context):
  # your code here, must return a string
  return 'my_company_id'
}
```

#### __`GET_SESSION_TOKEN`__

Type: `(event, context) => String`

`GET_SESSION_TOKEN` a function that takes AWS lambda `event` and `context` objects as arguments and returns a
session token (i.e. such as an API key).


```python
def get_session_token(event, context):
    # your code here, must return a string.
    return '23jdf0owekfmcn4u3qypxg09w4d8ayrcdx8nu2ng]s98y18cx98q3yhwmnhcfx43f'
```

#### __`GET_API_VERSION`__

Type: `(event, context) => String`

`GET_API_VERSION` is a function that takes AWS lambda `event` and `context` objects as arguments and
returns a string to tag requests with a specific version of your API.


```python
def get_api_version(event, context):
  # your code here. must return a string.
  return '1.0.0'
```

#### __`GET_METADATA`__

Type: `(event, context) => String`

`GET_METADATA` is a function that AWS lambda `event` and `context` objects as arguments and returns an object that allows you to add custom metadata that will be associated with the request. The metadata must be a simple python object that can be converted to JSON. For example, you may want to save a function_name, a trace_id, or request_context with the request.


```python
def get_metadata(event, context):
  # your code here:
  return {
        'trace_id': context.aws_request_id,
        'function_name': context.function_name,
        'request_context': event['requestContext']
    }
```

#### __`SKIP`__

Type: `(event, context) => Boolean`

`SKIP` is a function that takes AWS lambda `event` and `context` objects as arguments and returns true
if the event should be skipped (i.e. not logged)
<br/>_The default is shown below and skips requests to the root path "/"._


```python
def should_skip(event, context):
    # your code here. must return a boolean.
    return "/" in event['path']
```

#### __`MASK_EVENT_MODEL`__

Type: `MoesifEventModel => MoesifEventModel`

`MASK_EVENT_MODEL` is a function that takes the final Moesif event model (rather than the AWS lambda event/context objects) as an argument before being sent to Moesif. With maskContent, you can make modifications to headers or body such as removing certain header or body fields.

```python
def mask_event(eventmodel):
  # remove any field that you don't want to be sent to Moesif.
  return eventmodel
 ```

#### __`DEBUG`__

Type: `Boolean`

Set to true to print debug logs if you're having integegration issues. 

#### __`LOG_BODY`__

Type: `Boolean`

`LOG_BODY` is default to true, set to false to remove logging request and response body to Moesif.

## Examples

- [A complete example is available on GitHub](https://github.com/Moesif/moesif-aws-lambda-python-example).

## Other integrations

To view more documentation on integration options, please visit __[the Integration Options Documentation](https://www.moesif.com/docs/getting-started/integration-options/).__

[ico-built-for]: https://img.shields.io/badge/built%20for-aws%20lambda-blue.svg
[ico-license]: https://img.shields.io/badge/License-Apache%202.0-green.svg
[ico-source]: https://img.shields.io/github/last-commit/moesif/moesif-aws-lambda-python.svg?style=social

[link-built-for]: https://aws.amazon.com/lambda/
[link-license]: https://raw.githubusercontent.com/Moesif/moesif-aws-lambda-python/master/LICENSE
[link-source]: https://github.com/moesif/moesif-aws-lambda-python
