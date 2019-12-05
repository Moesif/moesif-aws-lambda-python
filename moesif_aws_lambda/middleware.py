from lambda_decorators import LambdaDecorator
from lambda_decorators import before, after, dump_json_body
from moesifapi.moesif_api_client import *
from moesifapi.api_helper import *
from moesifapi.exceptions.api_exception import *
from moesifapi.models import *
from .client_ip import ClientIp
from datetime import *
from urllib.parse import urlencode
import base64
import json
import os

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
            # Intialized the client
            if os.environ["MOESIF_APPLICATION_ID"]:
                self.api_client = MoesifAPIClient(os.environ["MOESIF_APPLICATION_ID"]).api
            else:
                raise Exception('Moesif Application ID is required in settings')

        def get_user_id(self, event, context):
            """Function to fetch UserId"""
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
                            print("can not fetch apiKey from cognitoIdentityId event, setting userId to None.")
            except Exception as e:
                if self.DEBUG:
                    print("can not execute identify_user function, please check moesif settings.")
                    print(e)
            return username
        
        def get_company_id(self, event, context):
            """Function to fetch CompanyId"""
            company_id = None
            try:
                identify_company = self.moesif_options.get("IDENTIFY_COMPANY")
                if identify_company is not None:
                    company_id = identify_company(event, context)
            except Exception as e:
                if self.DEBUG:
                    print("can not execute identify_company function, please check moesif settings.")
                    print(e)
            return company_id
        
        def process_request_body(self, raw_request_body):
            """Function to process Request body"""
            req_body = None
            req_transfer_encoding = None
            try:
                if 'isBase64Encoded' in raw_request_body and 'body' in raw_request_body and raw_request_body['isBase64Encoded'] and raw_request_body['body']:
                    req_body = raw_request_body['body']
                    req_transfer_encoding = 'base64'
                else:
                    if 'body' in raw_request_body and raw_request_body['body'] and isinstance(raw_request_body['body'], str):
                        req_body = json.loads(raw_request_body['body'])
                    else:
                        req_body = raw_request_body['body']
                    req_transfer_encoding = 'json'
            except Exception as e:
                if self.DEBUG:
                    print('Error while parsing request body')
                    print(e)
            return req_body, req_transfer_encoding

        def process_response_body(self, raw_response_body):
            """Function to process Response body"""
            resp_body = None
            resp_transfer_encoding = None
            try:
                if 'isBase64Encoded' in raw_response_body and 'body' in raw_response_body and raw_response_body['isBase64Encoded'] and raw_response_body['body']:
                    resp_body = raw_response_body['body']
                    resp_transfer_encoding = 'base64'
                else:
                    if 'body' in raw_response_body and raw_response_body['body'] and isinstance(raw_response_body['body'], str):
                        resp_body = json.loads(raw_response_body['body'])
                    else:
                        resp_body = raw_response_body['body']
                    resp_transfer_encoding = 'json'
            except Exception as e:
                if self.DEBUG:
                    print('Error while parsing response body')
                    print(e)
            return resp_body, resp_transfer_encoding

        def before(self, event, context):
            """This function runs before the handler is invoked, is passed the event & context and must return an event & context too."""
            # Request headers
            req_headers = {}
            try:
                if 'headers' in event:
                    req_headers = APIHelper.json_deserialize(event['headers'])
            except Exception as e:
                if self.DEBUG:
                    print('Error while fetching request headers')
                    print(e)

            # Request Time
            request_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
            
            # Request URI
            try:
                request_uri = event['headers']['X-Forwarded-Proto'] + '://' + event['headers']['Host'] + event['path'] + '?' + urlencode(event['queryStringParameters'])
            except:
                request_uri = '/'
            
            # Request Method
            try:
                request_verb = event['httpMethod']
            except:
                if self.DEBUG:
                    print('Request method should not be empty.')
            
            # Request Body
            req_body = None
            req_transfer_encoding = None
            try:
                if self.LOG_BODY and 'body' in event:
                    if event['body']:
                        req_body, req_transfer_encoding = self.process_request_body(event)
            except Exception as e:
                if self.DEBUG:
                    print('Error while fetching request body')
                    print(e)
            
            # Metadata
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
                                'request_context': event['requestContext']
                            }
                    except:
                        if self.DEBUG:
                            print("can not fetch default function_name and request_context from aws context, setting metadata to None.")
            except Exception as e:
                if self.DEBUG:
                    print("can not execute GET_METADATA function, please check moesif settings.")
                    print(e)
            
            # User Id
            self.user_id = self.get_user_id(event, context)

            # Company Id
            self.company_id = self.get_company_id(event, context)

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
                            print("can not fetch apiKey from aws event, setting session_token to None.")
            except Exception as e:
                if self.DEBUG:
                    print("can not execute GET_SESSION_TOKEN function, please check moesif settings.")
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
                            print("can not fetch default function_version from aws context, setting api_version to None.")
            except Exception as e:
                if self.DEBUG:
                    print("can not execute GET_API_VERSION function, please check moesif settings.")
                    print(e)
            
            # IpAddress
            ip_address = None
            try:
                if 'headers' in event and 'requestContext' in event and 'identity' in event['requestContext'] and 'sourceIp' in event['requestContext']['identity'] and event['requestContext']['identity']['sourceIp']:
                    ip_address = self.client_ip.get_client_address(event['headers'], event['requestContext']['identity']['sourceIp'])
            except Exception as e:
                if self.DEBUG:
                    print("Error while fetching Client Ip address, setting Request Ip address to None.")
                    print(e)

            # Event Request Object
            self.event_req = EventRequestModel(time = request_time,
                uri = request_uri,
                verb = request_verb,
                api_version = api_version,
                ip_address = ip_address,
                headers = req_headers,
                body = req_body,
                transfer_encoding = req_transfer_encoding)

            # Set/Save event and context for use Skip Event function
            self.event = event
            self.context = context
            
            # Return event, context
            return event, context
        
        def after(self, retval):
            """This function runs after the handler is invoked, is passed the response and must return an response too."""
            # Response body
            resp_body = None
            resp_transfer_encoding = None
            try:
                if self.LOG_BODY and 'body' in retval:
                    if retval['body']:
                        resp_body, resp_transfer_encoding = self.process_response_body(retval)
            except Exception as e:
                if self.DEBUG:
                    print('Error while fetching response body')
                    print(e)

            # Response headers
            resp_headers = {}
            try:
                if 'headers' in retval:
                    resp_headers = retval['headers']
            except Exception as e:
                if self.DEBUG:
                    print('Error while fetching response headers')
                    print(e)

            # Response status code
            try:
                status_code = retval['statusCode']
            except:
                if self.DEBUG:
                    print('Response status code should not be empty')

            # Event Response object
            event_rsp = EventResponseModel(time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                status = status_code,
                headers = resp_headers,
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
            except:
                if self.DEBUG:
                    print("Can not execute MASK_EVENT_MODEL function. Please check moesif settings.")

            # Skip Event
            try:
                skip_event = self.moesif_options.get('SKIP', None)
                if skip_event is not None:
                    if skip_event(self.event, self.context):
                        if self.DEBUG:
                            print('Skip sending event to Moesif')
                        return retval
            except:
                if self.DEBUG:
                    print("Having difficulty executing skip_event function. Please check moesif settings.")

            # Send event to Moesif
            event_send = self.api_client.create_event(event_model)
            if self.DEBUG:
                print('Event Sent successfully')
            
            # Send response
            return retval

    # Return log_data 
    return log_data
