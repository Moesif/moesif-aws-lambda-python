# Moesif AWS Lambda Middleware for Python documentation
by [Moesif](https://moesif.com), the [API analytics](https://www.moesif.com/features/api-analytics) and [API monetization](https://www.moesif.com/solutions/metered-api-billing) platform.


[![Built For][ico-built-for]][link-built-for]
[![Software License][ico-license]][link-license]
[![Source Code][ico-source]][link-source]

With Moesif Python middleware for AWS Lambda, you can automatically log API calls 
and send them to [Moesif](https://www.moesif.com) for API analytics and monitoring.
This middleware allows you to integrate Moesif's API analytics and 
API monetization features into your Python applications with minimal configuration.

> If you're new to Moesif, see [our Getting Started](https://www.moesif.com/docs/) resources to quickly get up and running.

## Who This Middleware is For

We've designed Moesif Python middleware for AWS Lambda for APIs that you host 
on AWS Lambda using Amazon API Gateway or Application Load Balancer
as a trigger. This middleware expects the
[Lambda proxy integration type](https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html). If you're using AWS Lambda with API Gateway, 
you are most likely using the proxy integration type.

## Prerequisites
Before using this middleware, make sure you have the following:

- [An active Moesif account](https://moesif.com/wrap)
- [A Moesif Application ID](#get-your-moesif-application-id)

### Get Your Moesif Application ID
After you log into [Moesif Portal](https://www.moesif.com/wrap), you can get your Moesif Application ID during the onboarding steps. You can always access the Application ID any time by following these steps from Moesif Portal after logging in:

1. Select the account icon to bring up the settings menu.
2. Select **Installation** or **API Keys**.
3. Copy your Moesif Application ID from the **Collector Application ID** field.
<img class="lazyload blur-up" src="images/app_id.png" width="700" alt="Accessing the settings menu in Moesif Portal">

## Install the Middleware
Install with `pip` using the following command:

```shell
pip install moesif_aws_lambda
```

## Configure the Middleware
See the available [configuration options](#configuration-options) to learn how to configure the middleware for your use case. 

## How to Use
### 1. Add the Middleware to your Lambda Application

```python
from moesif_aws_lambda.middleware import MoesifLogger
import json

moesif_options = {
    'LOG_BODY': True
}

@MoesifLogger(moesif_options)
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'isBase64Encoded': False,
        'body': json.dumps({
            'msg': 'Hello from Lambda!'
        }),
        'headers': {
            'Content-Type': 'application/json'
        }
    }
```

> __Important:__ Make sure you set the `body` field to a JSON-formatted string using `json.dumps()`. Otherwise,  API Gateway returns a `502 Bad Gateway` error response.

### 2. Set the MOESIF_APPLICATION_ID Environment Variable 
The middleware expects the `MOESIF_APPLICATION_ID` environment variable to be able to connect with your Moesif account and send analytics. This variable holds the value of [your Moesif Application ID](#get-your-moesif-application-id). For instructions on how to set environment variables in Lambda, see [Use Lambda environment variables to configure values in code](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html).

### 3. Deploy your Lambda Function 
To deploy your Lambda function code with Moesif AWS Lambda middleware, you must archive them in a zip file. For archiving instructions, see our [example Lambda function repository](https://github.com/Moesif/moesif-aws-lambda-python-example?tab=readme-ov-file#how-to-run-this-example). Then follow the instructions in [AWS Lambda docs to upload and deploy your Lambda function code as a zip file archive](https://docs.aws.amazon.com/lambda/latest/dg/configuration-function-zip.html).

### 4. Call your API
Finally, grab the URL to your API Gateway or Application Load Balancer and make some HTTP requests using a tool like Postman or cURL.

> In order for your events to log to Moesif, you must test using the Amazon API Gateway trigger. Do not invoke your Lambda directly using AWS Console as the payload won't contain a valid HTTP payload.

## Troubleshoot
For a general troubleshooting guide that can help you solve common problems, see [Server Troubleshooting Guide](https://www.moesif.com/docs/troubleshooting/server-troubleshooting-guide/).

Other troubleshooting supports:

- [FAQ](https://www.moesif.com/docs/faq/)
- [Moesif support email](mailto:support@moesif.com)

## Repository Structure

```
.
├── eventV1.json
├── eventV2.json
├── images/
├── lambda_function.py
├── LICENSE
├── moesif_aws_lambda/
├── package.sh
├── README.md
├── requirements.txt
├── setup.cfg
└── setup.py
```

These are the most important files:

- **`moesif_aws_lambda/middleware.py`**: the middleware library
- **`lambda_function.py`**: sample AWS Lambda function using the middleware

## Configuration Options
The following sections describe the available configuration options for this middleware. You can set these options in a Python object and then pass that object as argument to the `MoesifLogger` decorator. See [the sample AWS Lambda middleware function code](https://github.com/Moesif/moesif-aws-lambda-python/blob/857af6d4c12be8681e569f42317043c51acc2341/lambda_function.py#L6) for an example.

### `IDENTIFY_USER` 
<table>
  <tr>
   <th scope="col">
    Data type
   </th>
   <th scope="col">
    Parameters
   </th>
   <th scope="col">
    Return type
   </th>
  </tr>
  <tr>
   <td>
    Function
   </td>
   <td>
    <code>(event, context)</code>
   </td>
   <td>
    <code>String</code>
   </td>
  </tr>
</table>

A function that takes AWS Lambda `event` and `context` objects as arguments
and returns a user ID. This allows Moesif to attribute API requests to individual unique users
so you can understand who is calling your API. You can use this simultaneously with [`identify_company`](#identify_company)
to track both individual customers and the companies they are a part of.


```python
def identify_user(event, context):
  # your code here, must return a string
  return event["requestContext"]["identity"]["cognitoIdentityId"]
```

### `IDENTIFY_COMPANY` 

<table>
  <tr>
   <th scope="col">
    Data type
   </th>
   <th scope="col">
    Parameters
   </th>
   <th scope="col">
    Return type
   </th>
  </tr>
  <tr>
   <td>
    Function
   </td>
   <td>
    <code>(event, context)</code>
   </td>
   <td>
    <code>String</code>
   </td>
  </tr>
</table>

A function that takes AWS Lambda `event` and `context` objects as arguments
and returns a company ID. If you have a B2B business, this allows Moesif to attribute
API requests to specific companies or organizations so you can understand which accounts are
calling your API. You can use this simultaneously with [`identify_user`](#identify_user) to track both
individual customers and the companies they are a part of.


```python
def identify_company(event, context):
  # your code here, must return a string
  return '7890'
}
```

### `GET_SESSION_TOKEN` 

<table>
  <tr>
   <th scope="col">
    Data type
   </th>
   <th scope="col">
    Parameters
   </th>
   <th scope="col">
    Return type
   </th>
  </tr>
  <tr>
   <td>
    Function
   </td>
   <td>
    <code>(event, context)</code>
   </td>
   <td>
    <code>String</code>
   </td>
  </tr>
</table>

A function that takes AWS lambda `event` and `context` objects as arguments and returns a
session token such as an API key.

```python
def get_session_token(event, context):
    # your code here, must return a string.
    return 'XXXXXXXXX'
```

### `GET_API_VERSION` 
<table>
  <tr>
   <th scope="col">
    Data type
   </th>
   <th scope="col">
    Parameters
   </th>
   <th scope="col">
    Return type
   </th>
  </tr>
  <tr>
   <td>
    Function
   </td>
   <td>
    <code>(event, context)</code>
   </td>
   <td>
    <code>String</code>
   </td>
  </tr>
</table>

A function that takes AWS lambda `event` and `context` objects as arguments and
returns a string to tag requests with a specific version of your API.

```python
def get_api_version(event, context):
  # your code here. must return a string.
  return '1.0.0'
```

### `GET_METADATA` 
<table>
  <tr>
   <th scope="col">
    Data type
   </th>
   <th scope="col">
    Parameters
   </th>
   <th scope="col">
    Return type
   </th>
  </tr>
  <tr>
   <td>
    Function
   </td>
   <td>
    <code>(event, context)</code>
   </td>
   <td>
    <code>Object</code>
   </td>
  </tr>
</table>

A function that takes AWS lambda `event` and `context` objects as arguments and returns an object. 

This function allows you
to add custom metadata that Moesif can associate with the request. The metadata must be a simple Python object that can be converted to JSON. 

For example, you may want to save a virtual machine instance ID, a trace ID, or a tenant ID with the request.

```python
def get_metadata(event, context):
  # your code here:
  return {
        'trace_id': context.aws_request_id,
        'function_name': context.function_name,
        'request_context': event['requestContext']
    }
```

### `SKIP` 
<table>
  <tr>
   <th scope="col">
    Data type
   </th>
   <th scope="col">
    Parameters
   </th>
   <th scope="col">
    Return type
   </th>
  </tr>
  <tr>
   <td>
    Function
   </td>
   <td>
    <code>(event, context)</code>
   </td>
   <td>
    <code>Boolean</code>
   </td>
  </tr>
</table>

A function that takes AWS lambda `event` and `context` objects as arguments and returns `True`
if you want to skip the event. Skipping an event means Moesif doesn't log the event.

The following example skips requests to the root path `/`:


```python
def should_skip(event, context):
    # your code here. must return a boolean.
    return "/" in event['path']
```

### `MASK_EVENT_MODEL` 
<table>
  <tr>
   <th scope="col">
    Data type
   </th>
   <th scope="col">
    Parameters
   </th>
   <th scope="col">
    Return type
   </th>
  </tr>
  <tr>
   <td>
    Function
   </td>
   <td>
    <code>(MASK_EVENT_MODEL)</code>
   </td>
   <td>
    <code>MASK_EVENT_MODEL</code>
   </td>
  </tr>
</table>

A function that takes the final Moesif event model, rather than the AWS lambda event or context objects, as an
argument before the middleware sends the event model object to Moesif. 

With `MASK_EVENT_MODEL`, you can make modifications to headers or body such as
removing certain header or body fields.


```python
def mask_event(eventmodel):
  # remove any field that you don't want to be sent to Moesif.
  return eventmodel
```

For an example of how Moesif event model looks like, see the [`eventV1.json`](eventV1.json) and [`eventV2.json`](eventV2.json) files.

For more information about the different fields of Moesif's event model,
see [Moesif Python API documentation](https://www.moesif.com/docs/api?python).


### `DEBUG` 
<table>
  <tr>
   <th scope="col">
    Data type
   </th>
   <th scope="col">
    Default
   </th>
  </tr>
  <tr>
   <td>
    <code>Boolean</code>
   </td>
   <td>
    <code>undefined</code>
   </td>
  </tr>
</table>

Set to `True` to print debug logs if you're having integration issues.


### `LOG_BODY` 
<table>
  <tr>
   <th scope="col">
    Data type
   </th>
   <th scope="col">
    Default
   </th>
  </tr>
  <tr>
   <td>
    <code>Boolean</code>
   </td>
   <td>
    <code>True</code>
   </td>
  </tr>
</table>

Whether to log request and response body to Moesif.

## Optional: Capturing Outgoing API Calls
If you want to capture all outgoing API calls from your Python app to third parties like
Stripe or to your own dependencies, call `start_capture_outgoing()` to start capturing. This mechanism works by 
patching [Requests](https://requests.readthedocs.io/en/master/).

```python
from moesif_aws_lambda.middleware import *
start_capture_outgoing(moesif_options) # moesif_options are the configuration options.
```

### Options for Logging Outgoing Calls

The following options are available for capturing and logging outgoing calls. The request and response objects passed in correspond to the [`Request` and `Response` objects](https://requests.readthedocs.io/en/master/user/advanced/#request-and-response-objects) respectively of the Python Requests library.

#### `SKIP_OUTGOING` 
<table>
  <tr>
   <th scope="col">
    Data type
   </th>
   <th scope="col">
    Parameters
   </th>
   <th scope="col">
    Return type
   </th>
  </tr>
  <tr>
   <td>
    Function
   </td>
   <td>
    <code>(request, response)</code>
   </td>
   <td>
    <code>Boolean</code>
   </td>
  </tr>
</table>
Optional.

This function takes Requests [`Request` and `Response` objects](https://requests.readthedocs.io/en/latest/user/advanced/#request-and-response-objects) and returns `True` if you want to skip this particular event.

#### `IDENTIFY_USER_OUTGOING` 
<table>
  <tr>
   <th scope="col">
    Data type
   </th>
   <th scope="col">
    Parameters
   </th>
   <th scope="col">
    Return type
   </th>
  </tr>
  <tr>
   <td>
    Function
   </td>
   <td>
    <code>(request, response)</code>
   </td>
   <td>
    <code>String</code>
   </td>
  </tr>
</table>

Optional, but highly recommended.

This function takes Requests [`Request` and `Response` objects](https://requests.readthedocs.io/en/latest/user/advanced/#request-and-response-objects) and returns a string that represents 
the user ID used by your system. While Moesif tries to identify users automatically, different frameworks and your implementation might be very different. So we highly recommend that you accurately provide a 
user ID using this function.

#### `IDENTIFY_COMPANY_OUTGOING` 
<table>
  <tr>
   <th scope="col">
    Data type
   </th>
   <th scope="col">
    Parameters
   </th>
   <th scope="col">
    Return type
   </th>
  </tr>
  <tr>
   <td>
    Function
   </td>
   <td>
    <code>(request, response)</code>
   </td>
   <td>
    <code>String</code>
   </td>
  </tr>
</table>

Optional.

This function takes Requests [`Request` and `Response` objects](https://requests.readthedocs.io/en/latest/user/advanced/#request-and-response-objects) and returns a string that represents
 the company ID for this event.

#### `GET_METADATA_OUTGOING` 
<table>
  <tr>
   <th scope="col">
    Data type
   </th>
   <th scope="col">
    Parameters
   </th>
   <th scope="col">
    Return type
   </th>
  </tr>
  <tr>
   <td>
    Function
   </td>
   <td>
    <code>(request, response)</code>
   </td>
   <td>
    <code>Dictionary</code>
   </td>
  </tr>
</table>

Optional.

This function takes Requests [`Request` and `Response` objects](https://requests.readthedocs.io/en/latest/user/advanced/#request-and-response-objects) and
returns a Python dictionary. The dictionary must be such that it can be converted into 
valid JSON. This allows you to associate this event with custom metadata. 

For example, you may want to save a virtual machine instance ID, a trace ID, or a tenant ID with the request.

#### `GET_SESSION_TOKEN_OUTGOING` 

<table>
  <tr>
   <th scope="col">
    Data type
   </th>
   <th scope="col">
    Parameters
   </th>
   <th scope="col">
    Return type
   </th>
  </tr>
  <tr>
   <td>
    Function
   </td>
   <td>
    <code>(request, response)</code>
   </td>
   <td>
    <code>String</code>
   </td>
  </tr>
</table>

Optional.

This function takes Requests [`Request` and `Response` objects](https://requests.readthedocs.io/en/latest/user/advanced/#request-and-response-objects) and returns a string that represents the session token for this event. Similar to [user IDs](#identify_user_outgoing), Moesif tries to get the session token automatically. However, if you setup differs from the standard, this function can help tying up events together and help you replay the events.

#### `LOG_BODY_OUTGOING` 
<table>
  <tr>
   <th scope="col">
    Data type
   </th>
   <th scope="col">
    Default
   </th>
  </tr>
  <tr>
   <td>
    <code>Boolean</code>
   </td>
   <td>
    <code>True</code>
   </td>
  </tr>
</table>

Optional.

Whether to log request and response body to Moesif.

## Examples
See the [example AWS Lambda function](https://github.com/Moesif/moesif-aws-lambda-python/blob/master/lambda_function.py) that uses this middleware.

The following examples demonstrate how to add and update customer information.

### Update A Single User
To create or update a [user](https://www.moesif.com/docs/getting-started/users/) profile in Moesif, use the `update_user()` function.

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

The `metadata` field can contain any customer demographic or other info you want to store. Moesif only requires the `user_id` field.

For more information, see the function documentation in [Moesif Python API Reference](https://www.moesif.com/docs/api?python#update-a-user).

### Update Users in Batch
To update a list of [users](https://www.moesif.com/docs/getting-started/users/) in one batch, use the `update_users_batch()` function.

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

The `metadata` field can contain any customer demographic or other info you want to store. Moesif only requires the `user_id` field.

For more information, see the function documentation in [Moesif Python API Reference](https://www.moesif.com/docs/api?python#update-users-in-batch).

### Update A Single Company
To update a single [company](https://www.moesif.com/docs/getting-started/companies/), use the `update_company()` function.

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

The `metadata` field can contain any company demographic or other information you want to store. Moesif only requires the `company_id` field. For more information, see the function documentation in [Moesif Python API Reference](https://www.moesif.com/docs/api?python#update-a-company).

### Update Companies in Batch
To update a list of [companies](https://www.moesif.com/docs/getting-started/companies/) in one batch, use the `update_companies_batch()` function.

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

The `metadata` field can contain any company demographic or other information you want to store. Moesif only requires the `company_id` field. For more information, see the function documentation in [Moesif Python API Reference](https://www.moesif.com/docs/api?python#update-companies-in-batch).

## Additional Documentation
See [Moesif AWS Lambda Example for Python](https://github.com/Moesif/moesif-aws-lambda-python-example) for an example Lambda function using this middleware.

## How to Get Help
If you face any issues using this middleware, try the [troubheshooting guidelines](#troubleshoot). For further assistance, reach out to our [support team](mailto:support@moesif.com).

## Explore Other integrations
Explore other integration options from Moesif in [the Server Integration Options documentation](https://www.moesif.com/docs/server-integration/).

[ico-built-for]: https://img.shields.io/badge/built%20for-aws%20lambda-blue.svg
[ico-license]: https://img.shields.io/badge/License-Apache%202.0-green.svg
[ico-source]: https://img.shields.io/github/last-commit/moesif/moesif-aws-lambda-python.svg?style=social

[link-built-for]: https://aws.amazon.com/lambda/
[link-license]: https://raw.githubusercontent.com/Moesif/moesif-aws-lambda-python/master/LICENSE
[link-source]: https://github.com/moesif/moesif-aws-lambda-python
