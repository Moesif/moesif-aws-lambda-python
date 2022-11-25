# Moesif AWS Lambda Middleware

[![Built For][ico-built-for]][link-built-for]
[![Software License][ico-license]][link-license]
[![Source Code][ico-source]][link-source]

Middleware (Python) to automatically log API calls from AWS Lambda functions
and sends to [Moesif](https://www.moesif.com) for API analytics and log analysis. 

Designed for APIs that are hosted on AWS Lambda using Amazon API Gateway or Application Load Balancer
as a trigger.

This middleware expects the
[Lambda proxy integration type.](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-set-up-simple-proxy.html#api-gateway-set-up-lambda-proxy-integration-on-proxy-resource)
If you're using AWS Lambda with API Gateway, you are most likely using the proxy integration type.

## How to install

```shell
pip install moesif_aws_lambda
```

## How to use

### 1. Add middleware to your Lambda application.

```python
from moesif_aws_lambda.middleware import MoesifLogger

moesif_options = {
    'LOG_BODY': True
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

### 2. Set MOESIF_APPLICATION_ID environment variable 

Add a new environment variable with the name `MOESIF_APPLICATION_ID` and the value being your Moesif application id,
which can be found in the [_Moesif Portal_](https://www.moesif.com/).
After signing up for a Moesif account, your Moesif Application Id will be displayed during the onboarding steps. 

You can always find your Moesif Application Id at any time by logging 
into the [_Moesif Portal_](https://www.moesif.com/), click on the top right menu,
 and then clicking _Installation_.

### 3. Trigger your API
Grab the URL to your API Gateway or LB and make some calls using a tool like Postman or CURL. 

> In order for your event to log to Moesif, you must test using the Amazon API Gateway trigger. Do not invoke your lambda directly using AWS Console as the payload won't contain a valid HTTP payload.  

## Repo file structure

- `moesif_aws_lambda/middleware.py` the middleware library
- `lambda_function.py` sample AWS Lambda function using the middleware

## Optional: Capturing outgoing API calls
If you want to capture all outgoing API calls from your Python Lambda function to third parties like
Stripe or to your own dependencies, call `start_capture_outgoing()` to start capturing. This mechanism works by 
patching the [Requests](https://requests.readthedocs.io/en/master/) 

```python
from moesif_aws_lambda.middleware import *
start_capture_outgoing(moesif_options) # moesif_options are the configuration options.
```

## Configuration options

### __`IDENTIFY_USER`__

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

### __`IDENTIFY_COMPANY`__

Type: `(event, context) => String`

`IDENTIFY_COMPANY` is a function that takes AWS lambda `event` and `context` objects as arguments
and returns a company_id. If your business is B2B, this enables Moesif to attribute 
API requests to specific companies or organizations so you can understand which accounts are 
calling your API. This can be used simultaneously with `IDENTIFY_USER` to track both 
individual customers and the companies their a part of. 


```python
def identify_company(event, context):
  # your code here, must return a string
  return '7890'
}
```

### __`GET_SESSION_TOKEN`__

Type: `(event, context) => String`

`GET_SESSION_TOKEN` a function that takes AWS lambda `event` and `context` objects as arguments and returns a
session token (i.e. such as an API key).


```python
def get_session_token(event, context):
    # your code here, must return a string.
    return 'XXXXXXXXX'
```

### __`GET_API_VERSION`__

Type: `(event, context) => String`

`GET_API_VERSION` is a function that takes AWS lambda `event` and `context` objects as arguments and
returns a string to tag requests with a specific version of your API.


```python
def get_api_version(event, context):
  # your code here. must return a string.
  return '1.0.0'
```

### __`GET_METADATA`__

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

### __`SKIP`__

Type: `(event, context) => Boolean`

`SKIP` is a function that takes AWS lambda `event` and `context` objects as arguments and returns true
if the event should be skipped (i.e. not logged)
<br/>_The default is shown below and skips requests to the root path "/"._


```python
def should_skip(event, context):
    # your code here. must return a boolean.
    return "/" in event['path']
```

### __`MASK_EVENT_MODEL`__

Type: `MoesifEventModel => MoesifEventModel`

`MASK_EVENT_MODEL` is a function that takes the final Moesif event model (rather than the AWS lambda event/context objects) as an argument before being sent to Moesif. With maskContent, you can make modifications to headers or body such as removing certain header or body fields.

```python
def mask_event(eventmodel):
  # remove any field that you don't want to be sent to Moesif.
  return eventmodel
 ```

### __`DEBUG`__

Type: `Boolean`

Set to true to print debug logs if you're having integration issues. 

### __`LOG_BODY`__

Type: `Boolean`

`LOG_BODY` is default to true, set to false to remove logging request and response body to Moesif.

## Options for logging outgoing calls

The options below are applied to outgoing API calls. The request and response objects passed in are  [Requests](https://requests.readthedocs.io/en/master/user/advanced/#request-and-response-objects) request and [Response](https://requests.readthedocs.io/en/master/user/advanced/#request-and-response-objects) response objects.

### __`SKIP_OUTGOING`__
(optional) _(req, res) => boolean_, a function that takes a [Requests](https://requests.readthedocs.io/en/master/) request and response,
and returns true if you want to skip this particular event.

### __`IDENTIFY_USER_OUTGOING`__
(optional, but highly recommended) _(req, res) => string_, a function that takes [Requests](https://requests.readthedocs.io/en/master/) request and response, and returns a string that is the user id used by your system. While Moesif tries to identify users automatically,
but different frameworks and your implementation might be very different, it would be helpful and much more accurate to provide this function.

### __`IDENTIFY_COMPANY_OUTGOING`__
(optional) _(req, res) => string_, a function that takes [Requests](https://requests.readthedocs.io/en/master/) request and response, and returns a string that is the company id for this event.

### __`GET_METADATA_OUTGOING`__
(optional) _(req, res) => dictionary_, a function that takes [Requests](https://requests.readthedocs.io/en/master/) request and response, and
returns a dictionary (must be able to be encoded into JSON). This allows
to associate this event with custom metadata. For example, you may want to save a VM instance_id, a trace_id, or a tenant_id with the request.

### __`GET_SESSION_TOKEN_OUTGOING`__
(optional) _(req, res) => string_, a function that takes [Requests](https://requests.readthedocs.io/en/master/) request and response, and returns a string that is the session token for this event. Again, Moesif tries to get the session token automatically, but if you setup is very different from standard, this function will be very help for tying events together, and help you replay the events.

### __`LOG_BODY_OUTGOING`__
(optional) _boolean_, default True, Set to False to remove logging request and response body.

## Update User

### Update A Single User
Create or update a user profile in Moesif.
The metadata field can be any customer demographic or other info you want to store.
Only the `user_id` field is required.
For details, visit the [Python API Reference](https://www.moesif.com/docs/api?python#update-a-user).

```python
from moesif_aws_lambda.middleware import *

moesif_options = {
    'LOG_BODY': True,
    'DEBUG': True,
}

# Only user_id is required.
# Campaign object is optional, but useful if you want to track ROI of acquisition channels
# See https://www.moesif.com/docs/api#users for campaign schema
# metadata can be any custom object
user = {
  'user_id': '12345',
  'company_id': '67890', # If set, associate user with a company object
  'campaign': {
    'utm_source': 'google',
    'utm_medium': 'cpc',
    'utm_campaign': 'adwords',
    'utm_term': 'api+tooling',
    'utm_content': 'landing'
  },
  'metadata': {
    'email': 'john@acmeinc.com',
    'first_name': 'John',
    'last_name': 'Doe',
    'title': 'Software Engineer',
    'sales_info': {
        'stage': 'Customer',
        'lifetime_value': 24000,
        'account_owner': 'mary@contoso.com'
    },
  }
}

update_user(user, moesif_options)
```

### Update Users in Batch
Similar to update_user, but used to update a list of users in one batch.
Only the `user_id` field is required.
For details, visit the [Python API Reference](https://www.moesif.com/docs/api?python#update-users-in-batch).

```python
from moesif_aws_lambda.middleware import *

moesif_options = {
    'LOG_BODY': True,
    'DEBUG': True,
}

userA = {
  'user_id': '12345',
  'company_id': '67890', # If set, associate user with a company object
  'metadata': {
    'email': 'john@acmeinc.com',
    'first_name': 'John',
    'last_name': 'Doe',
    'title': 'Software Engineer',
    'sales_info': {
        'stage': 'Customer',
        'lifetime_value': 24000,
        'account_owner': 'mary@contoso.com'
    },
  }
}

userB = {
  'user_id': '54321',
  'company_id': '67890', # If set, associate user with a company object
  'metadata': {
    'email': 'mary@acmeinc.com',
    'first_name': 'Mary',
    'last_name': 'Jane',
    'title': 'Software Engineer',
    'sales_info': {
        'stage': 'Customer',
        'lifetime_value': 48000,
        'account_owner': 'mary@contoso.com'
    },
  }
}
update_users_batch([userA, userB], moesif_options)
```

## Update Company

### Update A Single Company
Create or update a company profile in Moesif.
The metadata field can be any company demographic or other info you want to store.
Only the `company_id` field is required.
For details, visit the [Python API Reference](https://www.moesif.com/docs/api?python#update-a-company).

```python
from moesif_aws_lambda.middleware import *

moesif_options = {
    'LOG_BODY': True,
    'DEBUG': True,
}

# Only company_id is required.
# Campaign object is optional, but useful if you want to track ROI of acquisition channels
# See https://www.moesif.com/docs/api#update-a-company for campaign schema
# metadata can be any custom object
company = {
  'company_id': '67890',
  'company_domain': 'acmeinc.com', # If domain is set, Moesif will enrich your profiles with publicly available info
  'campaign': {
    'utm_source': 'google',
    'utm_medium': 'cpc',
    'utm_campaign': 'adwords',
    'utm_term': 'api+tooling',
    'utm_content': 'landing'
  },
  'metadata': {
    'org_name': 'Acme, Inc',
    'plan_name': 'Free',
    'deal_stage': 'Lead',
    'mrr': 24000,
    'demographics': {
        'alexa_ranking': 500000,
        'employee_count': 47
    },
  }
}

update_company(company, moesif_options)
```

### Update Companies in Batch
Similar to update_company, but used to update a list of companies in one batch.
Only the `company_id` field is required.
For details, visit the [Python API Reference](https://www.moesif.com/docs/api?python#update-companies-in-batch).

```python
from moesif_aws_lambda.middleware import *

moesif_options = {
    'LOG_BODY': True,
    'DEBUG': True,
}

companyA = {
  'company_id': '67890',
  'company_domain': 'acmeinc.com', # If domain is set, Moesif will enrich your profiles with publicly available info
  'metadata': {
    'org_name': 'Acme, Inc',
    'plan_name': 'Free',
    'deal_stage': 'Lead',
    'mrr': 24000,
    'demographics': {
        'alexa_ranking': 500000,
        'employee_count': 47
    },
  }
}

companyB = {
  'company_id': '09876',
  'company_domain': 'contoso.com', # If domain is set, Moesif will enrich your profiles with publicly available info
  'metadata': {
    'org_name': 'Contoso, Inc',
    'plan_name': 'Free',
    'deal_stage': 'Lead',
    'mrr': 48000,
    'demographics': {
        'alexa_ranking': 500000,
        'employee_count': 53
    },
  }
}

update_companies_batch([companyA, companyB], moesif_options)
```

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
