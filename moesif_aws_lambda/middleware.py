from lambda_decorators import LambdaDecorator
from lambda_decorators import before, after, dump_json_body
from moesifapi.moesif_api_client import *
from moesifapi.api_helper import *
from moesifapi.exceptions.api_exception import *
from moesifapi.models import *
from .client_ip import ClientIp
from .update_companies import Company
from .update_users import User
from . import global_variable as gv

from datetime import *
import base64
import json
import os
from pprint import pprint

import random
import math
import binascii
import re

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
from moesifpythonrequest.start_capture.start_capture import StartCapture
from datetime import datetime


def get_time_took_in_ms(start_time, end_time):
    return (end_time - start_time).total_seconds() * 1000


def start_capture_outgoing(moesif_options):
    try:
        if moesif_options.get('DEBUG', False):
            print('[moesif] Start capturing outgoing requests')

        # Start capturing outgoing requests
        moesif_options['APPLICATION_ID'] = os.environ["MOESIF_APPLICATION_ID"]
        StartCapture().start_capture_outgoing(moesif_options)

        if moesif_options.get('DEBUG', False):
            print("[moesif] end capturing moesif options")
    except Exception as e:
        print('Error while starting to capture the outgoing events')
        print(e)
    return


# Initialized the client
api_client = gv.api_client


def update_user(user_profile, moesif_options):
    User().update_user(user_profile, api_client, moesif_options)


def update_users_batch(user_profiles, moesif_options):
    User().update_users_batch(user_profiles, api_client, moesif_options)


def update_company(company_profile, moesif_options):
    Company().update_company(company_profile, api_client, moesif_options)


def update_companies_batch(companies_profiles, moesif_options):
    Company().update_companies_batch(companies_profiles, api_client, moesif_options)


def MoesifLogger(moesif_options):
    class log_data(LambdaDecorator):
        def __init__(self, handler):
        
            self.event_req = None
            self.handler = handler
            self.moesif_options = moesif_options
            self.metadata = None
            self.session_token = None
            self.client_ip = ClientIp()
            self.user_id = None
            self.company_id = None
            self.LOG_BODY = self.moesif_options.get('LOG_BODY', True)
            self.DEBUG = self.moesif_options.get('DEBUG', False)
            self.event = None
            self.context = None
            self.payload_version = None

            # Set the client
            self.api_client = api_client

        def clear_state(self):
            """Function to clear state of local variable"""
            self.event = None
            self.context = None
            self.payload_version = None
            self.event_req = None
            self.metadata = None
            self.session_token = None
            self.user_id = None
            self.company_id = None

        def is_payload_format_version_1_0(cls, payload_format_version):
            """Function to check if the payload format version is 1.0 (old) or 2.0 (new) """
            return payload_format_version == "1.0"

        def get_user_id(self, event, context):
            """Function to fetch UserId"""
            start_time_get_user_id = datetime.utcnow()
            username = None
            try:
                identify_user = self.moesif_options.get("IDENTIFY_USER")
                if identify_user is not None:
                    username = identify_user(event, context)
                else:
                    try:
                        if 'requestContext' in event and 'identity' in event["requestContext"] and 'cognitoIdentityId' in event["requestContext"]["identity"]:
                            rc_identity_id = event["requestContext"]["identity"]["cognitoIdentityId"]
                            if rc_identity_id:
                                username = rc_identity_id
                    except:
                        if self.DEBUG:
                            print("[moesif] cannot fetch apiKey from cognitoIdentityId event, setting userId to None.")
            except Exception as e:
                if self.DEBUG:
                    print("[moesif] cannot execute identify_user function, please check moesif settings.")
                    print(e)
            end_time_get_user_id = datetime.utcnow()
            if self.DEBUG:
                print("[moesif] Time took in fetching user id in millisecond - " + str(get_time_took_in_ms(start_time_get_user_id, end_time_get_user_id)))
            return username

        def get_company_id(self, event, context):
            """Function to fetch CompanyId"""
            start_time_get_company_id = datetime.utcnow()
            company_id = None
            try:
                identify_company = self.moesif_options.get("IDENTIFY_COMPANY")
                if identify_company is not None:
                    company_id = identify_company(event, context)
            except Exception as e:
                if self.DEBUG:
                    print("[moesif] cannot execute identify_company function, please check moesif settings.")
                    print(e)
            end_time_get_company_id = datetime.utcnow()
            if self.DEBUG:
                print("[moesif] Time took in fetching company id in millisecond - " + str(get_time_took_in_ms(start_time_get_company_id, end_time_get_company_id)))
            return company_id

        def build_uri(self, event, payload_format_version_1_0):

            uri = ''
            try: 
                uri = event['headers'].get('X-Forwarded-Proto', event['headers'].get('x-forwarded-proto', 'http')) + '://' + event['headers'].get('Host', event['headers'].get('host', 'localhost'))
            except Exception as e:
                if self.DEBUG:
                    print("[moesif] cannot read HTTP headers X-Forwarded-Proto or Host. Ensure event triggered via external URL")
                    print(e)

            if payload_format_version_1_0:
                uri = uri + event.get('path', '/')
                if event.get('multiValueQueryStringParameters', {}):
                    uri = uri + '?' + urlencode(event['multiValueQueryStringParameters'], doseq=True)
                elif event.get('queryStringParameters', {}):
                    uri = uri + '?' + urlencode(event['queryStringParameters'])
            else:
                uri = uri + event.get('rawPath', '/')
                if event.get('rawQueryString', {}):
                    uri = uri + '?' + event['rawQueryString']
            return uri

        def is_base64_str(self, data):
            """Checks if `data` is a valid base64-encoded string."""
            if not isinstance(data, str):
                return False
            if len(data) % 4 != 0:
                return False
            
            b64_regex = re.compile("^[A-Za-z0-9+/]+={0,2}$")

            if (not b64_regex.fullmatch(data)):
                return False
            
            try:
                _ = base64.b64decode(data)
                return True
            except binascii.Error:
                return False
            
        def base64_body(cls, data):
            """Function to transfer body into base64 encoded"""
            body = base64.b64encode(str(data).encode("utf-8"))
            if isinstance(body, str):
                return str(body).encode("utf-8"), 'base64'
            elif isinstance(body, (bytes, bytearray)):
                return str(body, "utf-8"), 'base64'
            else:
                return str(body), 'base64'
        
        def safe_json_parse(self, body):
            """Tries to parse the `body` as JSON safely.
            Returns the formatted body and the appropriate `transfer_encoding`. 
            """
            try:
                if isinstance(body, (dict, list)):
                    # If body is an instance of either a dictionary of list, 
                    # we can return it as is.
                    return body, "json"
                elif isinstance(body, bytes):
                    body_str = body.decode()
                    parsed_body = json.loads(body_str)
                    return parsed_body, "json"
                else:
                    parsed_body = json.loads(body)
                    return parsed_body, "json"
 
            except (json.JSONDecodeError, TypeError, ValueError, UnicodeError) as error:
                return self.base64_body(body)

        def process_body(self, body_wrapper):
            """Function to process body"""

            if self.LOG_BODY and isinstance(body_wrapper, dict) and 'body' not in body_wrapper:
                return body_wrapper, 'json'

            if self.LOG_BODY and not isinstance(body_wrapper, dict) and 'body' not in body_wrapper and isinstance(body_wrapper, str):
                return self.base64_body(body_wrapper)

            if not (self.LOG_BODY and isinstance(body_wrapper, dict) and body_wrapper.get('body')):
                return None, 'json'

            body = None
            transfer_encoding = None

            try:
                if body_wrapper.get('isBase64Encoded', False) and self.is_base64_str(body_wrapper.get('body')):
                        body = body_wrapper.get('body')
                        transfer_encoding = 'base64'
                else:
                    body, transfer_encoding = self.safe_json_parse(body_wrapper.get('body'))
            except Exception as e:
                    return self.base64_body(body_wrapper['body'])

            return body, transfer_encoding

        def before(self, event, context):
            """This function runs before the handler is invoked, is passed the event & context and must return an event & context too."""

            start_time_before_handler_function = datetime.utcnow()
            if self.DEBUG:
                print('[moesif] : [before] Incoming Event:')
                print(json.dumps(event))

            # Clear the state of the local variables
            self.clear_state()

            # Get the payload format version
            # https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
            self.payload_version = event.get('version', '1.0')

            # Set/Save event and context for use Skip Event function
            self.event = event
            self.context = context

            # Request Method
            if self.is_payload_format_version_1_0(self.payload_version):
                request_verb = event.get('httpMethod')
            else:
                request_verb = event.get('requestContext', {}).get('http', {}).get('method')
            if request_verb is None:
                print('[moesif] : [before] AWS Lambda trigger must be a Load Balancer or API Gateway See https://docs.aws.amazon.com/lambda/latest/dg/services-alb.html or https://docs.aws.amazon.com/lambda/latest/dg/with-on-demand-https.html.')
                self.event = None
                self.context = None
                self.payload_version = None
                return event, context

            # Request headers
            req_headers = event.get('headers', {})
            try:
                if isinstance(req_headers, str):
                    req_headers = APIHelper.json_deserialize(req_headers)
            except Exception as e:
                if self.DEBUG:
                    print('[moesif] Error while fetching request headers')
                    print(e)

            # Request Time
            if self.is_payload_format_version_1_0(self.payload_version):
                epoch = event and event.get('requestContext', {}).get('requestTimeEpoch')
            else:
                epoch = event and  event.get('requestContext', {}).get('timeEpoch')
            if epoch is not None:
                # Dividing by 1000 to convert from ms to seconds and `.0` to preserve millisecond precision 
                request_time = datetime.utcfromtimestamp(epoch/1000.0)
            else:
                request_time = datetime.utcnow()

            # Request Body
            req_body, req_transfer_encoding = self.process_body(event)

            # Metadata
            start_time_get_metadata = datetime.utcnow()
            try:
                get_meta = self.moesif_options.get("GET_METADATA")
                if get_meta is not None:
                    self.metadata = get_meta(event, context)
                else:
                    try:
                        if context.aws_request_id and context.function_name and 'requestContext' in event:
                            self.metadata = {
                                'trace_id': str(context.aws_request_id),
                                'function_name': context.function_name,
                                'request_context': event['requestContext'],
                                # Lambda context object - https://docs.aws.amazon.com/lambda/latest/dg/python-context.html
                                'context': {
                                    'aws_request_id': str(getattr(context, 'aws_request_id', ''))
                                }
                            }
                    except:
                        if self.DEBUG:
                            print("[moesif] cannot fetch default function_name and request_context from aws context, setting metadata to None.")
            except Exception as e:
                if self.DEBUG:
                    print("[moesif] cannot execute GET_METADATA function, please check moesif settings.")
                    print(e)
            end_time_get_metadata = datetime.utcnow()
            if self.DEBUG:
                print("[moesif] Time took in fetching metadata in millisecond - " + str(get_time_took_in_ms(start_time_get_metadata, end_time_get_metadata)))

            # User Id
            start_time_identify_user = datetime.utcnow()
            self.user_id = self.get_user_id(event, context)
            end_time_identify_user = datetime.utcnow()
            if self.DEBUG:
                print("[moesif] Time took in identifying the user in millisecond - " + str(get_time_took_in_ms(start_time_identify_user, end_time_identify_user)))

            # Company Id
            start_time_identify_company = datetime.utcnow()
            self.company_id = self.get_company_id(event, context)
            end_time_identify_company = datetime.utcnow()
            if self.DEBUG:
                print("[moesif] Time took in identifying the company in millisecond - " + str(get_time_took_in_ms(start_time_identify_company, end_time_identify_company)))

            # Session Token 
            try:
                get_token = self.moesif_options.get("GET_SESSION_TOKEN")
                if get_token is not None:
                    self.session_token = get_token(event, context)
                else:
                    try:
                        if 'requestContext' in event and 'identity' in event['requestContext'] and 'apiKey' in event['requestContext']['identity'] and event['requestContext']['identity']['apiKey']:
                            rc_api_key = event['requestContext']['identity']['apiKey']
                            if rc_api_key:
                                self.session_token = rc_api_key
                    except KeyError:
                        if self.DEBUG:
                            print("[moesif] cannot fetch apiKey from aws event, setting session_token to None.")
            except Exception as e:
                if self.DEBUG:
                    print("[moesif] cannot execute GET_SESSION_TOKEN function, please check moesif settings.")
                    print(e)

            # Api Version
            api_version = None
            try:
                get_version = self.moesif_options.get("GET_API_VERSION")
                if get_version is not None:
                    api_version = get_version(event, context)
                else:
                    try:
                        if context.function_version:
                            api_version = context.function_version
                    except KeyError:
                        if self.DEBUG:
                            print("[moesif] cannot fetch default function_version from aws context, setting api_version to None.")
            except Exception as e:
                if self.DEBUG:
                    print("[moesif] cannot execute GET_API_VERSION function, please check moesif settings.")
                    print(e)

            # IpAddress
            if self.is_payload_format_version_1_0(self.payload_version):
                ip_address = event.get('requestContext', {}).get('identity', {}).get('sourceIp', None)
            else:
                ip_address = event.get('requestContext', {}).get('http', {}).get('sourceIp', None)

            # Event Request Object
            self.event_req = EventRequestModel(time = request_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                uri = self.build_uri(event, self.is_payload_format_version_1_0(self.payload_version)),
                verb = request_verb,
                api_version = api_version,
                ip_address = self.client_ip.get_client_address(event['headers'], ip_address),
                headers = req_headers,
                body = req_body,
                transfer_encoding = req_transfer_encoding)

            end_time_before_handler_function = datetime.utcnow()
            if self.DEBUG:
                print("[moesif] Time took before the handler is invoked in millisecond - " + str(get_time_took_in_ms(start_time_before_handler_function, end_time_before_handler_function)))
            # Return event, context
            return event, context

        def after(self, retval):
            """This function runs after the handler is invoked, is passed the response and must return an response too."""
            
            start_time_after_handler_function = datetime.utcnow()
            event_send = None
            if self.event is not None:
                # Response body
                resp_body, resp_transfer_encoding = self.process_body(retval)

                # Event Response object
                event_rsp = EventResponseModel(time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                    status = retval.get('statusCode', 599) if 'statusCode' in retval else 200,
                    headers = retval.get('headers', {}) if 'headers' in retval else {"content-type": "application/json" },
                    body = resp_body,
                    transfer_encoding = resp_transfer_encoding)

                # Event object
                event_model = EventModel(request = self.event_req,
                    response = event_rsp,
                    user_id = self.user_id,
                    company_id = self.company_id,
                    session_token = self.session_token,
                    metadata = self.metadata)

                # Mask Event Model
                try:
                    mask_event_model = self.moesif_options.get('MASK_EVENT_MODEL', None)
                    if mask_event_model is not None:
                        event_model = mask_event_model(event_model)
                except Exception as e:
                    if self.DEBUG:
                        print("[moesif] cannot execute MASK_EVENT_MODEL function. Please check moesif settings.", e)

                # Skip Event
                try:
                    skip_event = self.moesif_options.get('SKIP', None)
                    if skip_event is not None:
                        if skip_event(self.event, self.context):
                            if self.DEBUG:
                                print('[moesif] Skip sending event to Moesif')
                            return retval
                except Exception as e:
                    if self.DEBUG:
                        print("[moesif] Having difficulty executing skip_event function. Please check moesif settings.", e)

                # Add direction field
                event_model.direction = "Incoming"

                # Send event to Moesif
                if self.DEBUG:
                    print('[moesif] : [after] Moesif Event Model:')
                    print(json.dumps(self.event))

                # Sampling Rate
                try:
                    random_percentage = random.random() * 100
                    gv.sampling_percentage = gv.app_config.get_sampling_percentage(
                        event_model,
                        json.loads(gv.config.raw_body),
                        self.user_id,
                        self.company_id,
                    )

                    if gv.sampling_percentage >= random_percentage:
                        event_model.weight = 1 if gv.sampling_percentage == 0 else math.floor(
                            100 / gv.sampling_percentage)

                        if datetime.utcnow() > gv.last_updated_time + timedelta(seconds=gv.refresh_config_time_seconds):
                            event_send = self.api_client.create_event(event_model)
                        else:
                            self.api_client.create_event(event_model)

                        try:
                            # Check if we need to update config
                            new_config_etag = event_send['x-moesif-config-etag']
                            if gv.config_etag is None or (gv.config_etag != new_config_etag):
                                gv.config_etag = new_config_etag
                                gv.config = gv.app_config.get_config(self.api_client, self.DEBUG)
                        except (KeyError, TypeError, ValueError) as ex:
                            # ignore the error because "event_send" is not set in non-blocking call
                            pass
                        finally:
                            gv.last_updated_time = datetime.utcnow()

                    else:
                        if self.DEBUG:
                            print("Skipped Event due to sampling percentage: " + str(
                                gv.sampling_percentage) + " and random percentage: " + str(random_percentage))
                except Exception as ex:
                    print("[moesif] Error when fetching sampling rate from app config", ex)

            end_time_after_handler_function = datetime.utcnow()
            if self.DEBUG:
                print("[moesif] Time took after the handler is invoked in millisecond - " + str(get_time_took_in_ms(start_time_after_handler_function, end_time_after_handler_function)))

            # Send response
            return retval

    # Return log_data 
    return log_data
