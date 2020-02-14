from lambda_decorators import LambdaDecorator
from lambda_decorators import before, after, dump_json_body
from moesifapi.moesif_api_client import *
from moesifapi.api_helper import *
from moesifapi.exceptions.api_exception import *
from moesifapi.models import *
from .client_ip import ClientIp
from .update_companies import Company
from .update_users import User
from datetime import *
import base64
import json
import os
from pprint import pprint
import base64
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

# Initialized the client
if os.environ["MOESIF_APPLICATION_ID"]:
    api_client = MoesifAPIClient(os.environ["MOESIF_APPLICATION_ID"]).api
else:
    raise Exception('Moesif Application ID is required in settings')

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
            
            # Intialized the client
            if os.environ.get("MOESIF_APPLICATION_ID"):
                self.api_client = MoesifAPIClient(os.environ["MOESIF_APPLICATION_ID"]).api
            else:
                raise Exception('Moesif Application ID is required in settings')

        def clear_state(self):
            """Function to clear state of local variable"""
            self.event = None
            self.context = None
            self.event_req = None
            self.metadata = None
            self.session_token = None
            self.user_id = None
            self.company_id = None

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
                            print("MOESIF can not fetch apiKey from cognitoIdentityId event, setting userId to None.")
            except Exception as e:
                if self.DEBUG:
                    print("MOESIF can not execute identify_user function, please check moesif settings.")
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
                    print("MOESIF can not execute identify_company function, please check moesif settings.")
                    print(e)
            return company_id
        
        def build_uri(self, event):

            uri = event['headers'].get('X-Forwarded-Proto', event['headers'].get('x-forwarded-proto', 'http')) + '://' + event['headers'].get('Host', event['headers'].get('host', 'localhost')) + event.get('path', '/')
            
            if event.get('multiValueQueryStringParameters', {}):
                uri = uri + '?' + urlencode(event['multiValueQueryStringParameters'], doseq=True) 
            elif event.get('queryStringParameters', {}):
                uri = uri + '?' + urlencode(event['queryStringParameters']) 
            return uri

        def process_body(self, body_wrapper):
            """Function to process body"""
            if not (self.LOG_BODY and body_wrapper.get('body')):
                return None, 'json'

            body = None
            transfer_encoding = None
            try:
                if body_wrapper.get('isBase64Encoded', False):
                    body = body_wrapper.get('body')
                    transfer_encoding = 'base64'
                else:
                    if isinstance(body_wrapper['body'], str):
                        body = json.loads(body_wrapper.get('body'))
                    else:
                        body = body_wrapper.get('body')
                    transfer_encoding = 'json'
            except Exception as e:
                body = base64.b64encode(str(body_wrapper['body']).encode("utf-8"))
                if isinstance(body, str):
                    return str(body).encode("utf-8"), 'base64'
                elif isinstance(body, (bytes, bytearray)):
                    return str(body, "utf-8"), 'base64'
                else:
                    return str(body), 'base64'
            return body, transfer_encoding

        def before(self, event, context):
            """This function runs before the handler is invoked, is passed the event & context and must return an event & context too."""

            # Clear the state of the local variables
            self.clear_state()

            # Set/Save event and context for use Skip Event function
            self.event = event
            self.context = context

            # Request Method
            request_verb = event.get('httpMethod')
            if request_verb is None:
                print('MOESIF: [before] AWS Lambda trigger must be a Load Balancer or API Gateway See https://docs.aws.amazon.com/lambda/latest/dg/services-alb.html or https://docs.aws.amazon.com/lambda/latest/dg/with-on-demand-https.html.')
                self.event = None
                self.context = None
                return event, context

            # Request headers
            req_headers = {}
            try:
                if 'headers' in event:
                    req_headers = APIHelper.json_deserialize(event['headers'])
            except Exception as e:
                if self.DEBUG:
                    print('MOESIF Error while fetching request headers')
                    print(e)

            # Request Time
            epoch = event and event.get('request_context', {}).get('requestTimeEpoch')
            if epoch is not None: 
                request_time = datetime.utcfromtimestamp(epoch)
            else:
                request_time = datetime.utcnow()
            
            # Request Body
            req_body, req_transfer_encoding = self.process_body(event)
            
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
                                'request_context': event['requestContext'],
                                'context': context
                            }
                    except:
                        if self.DEBUG:
                            print("MOESIF can not fetch default function_name and request_context from aws context, setting metadata to None.")
            except Exception as e:
                if self.DEBUG:
                    print("MOESIF can not execute GET_METADATA function, please check moesif settings.")
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
                            print("MOESIF can not fetch apiKey from aws event, setting session_token to None.")
            except Exception as e:
                if self.DEBUG:
                    print("MOESIF can not execute GET_SESSION_TOKEN function, please check moesif settings.")
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
                            print("MOESIF can not fetch default function_version from aws context, setting api_version to None.")
            except Exception as e:
                if self.DEBUG:
                    print("MOESIF can not execute GET_API_VERSION function, please check moesif settings.")
                    print(e)
            
            # IpAddress
            ip_address = event.get('requestContext', {}).get('identity', {}).get('sourceIp', None)

            # Event Request Object
            self.event_req = EventRequestModel(time = request_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                uri = self.build_uri(event),
                verb = request_verb,
                api_version = api_version,
                ip_address = self.client_ip.get_client_address(event['headers'], ip_address),
                headers = req_headers,
                body = req_body,
                transfer_encoding = req_transfer_encoding)

            # Return event, context
            return event, context
        
        def after(self, retval):
            """This function runs after the handler is invoked, is passed the response and must return an response too."""
            
            if self.event is not None:
                # Response body
                resp_body, resp_transfer_encoding = self.process_body(retval)

                # Event Response object
                event_rsp = EventResponseModel(time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                    status = retval.get('statusCode', 599),
                    headers = retval.get('headers', {}),
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
                        print("MOESIF Can not execute MASK_EVENT_MODEL function. Please check moesif settings.")

                # Skip Event
                try:
                    skip_event = self.moesif_options.get('SKIP', None)
                    if skip_event is not None:
                        if skip_event(self.event, self.context):
                            if self.DEBUG:
                                print('MOESIF Skip sending event to Moesif')
                            return retval
                except:
                    if self.DEBUG:
                        print("MOESIF Having difficulty executing skip_event function. Please check moesif settings.")

                # Add direction field
                event_model.direction = "Incoming"

                # Send event to Moesif
                if self.DEBUG:
                    print('Moesif Event Model:')
                    print(json.dumps(self.event))
                
                event_send = self.api_client.create_event(event_model)
                if self.DEBUG:
                    print('MOESIF ' + str(event_send))

            # Send response
            return retval

    # Return log_data 
    return log_data
