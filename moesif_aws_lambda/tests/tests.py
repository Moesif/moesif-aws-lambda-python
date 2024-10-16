import json
import unittest
import base64
from ..middleware import MoesifLogger

moesif_options = {
    "LOG_BODY": True,
    "DEBUG": True
}


def lambda_handler(event, context):

    return {
        "statusCode": 200,
        "isBase64Encoded": False,
        "body": json.dumps({"msg": "Hello from Lambda!"}),
        "headers": {"Content-Type": "application/json"},
    }


class TestStrIsBase64(unittest.TestCase):
    def test_valid_base64_encoded_str(self):
        """
        Tests that `is_str_base64` returns `True` for a valid base64-encoded
        string.
        """
        valid_base64 = "eyJmb28iOiJiYXIifQ=="
        moesif = MoesifLogger(moesif_options)
        self.assertTrue(moesif.is_base64_str(self=moesif, data=valid_base64))

    def test_invalid_base64_encoded_str(self):
        """
        Tests that `is_str_base64` returns `False` for an invalid base64-encoded
        string.
        """
        invalid_base64 = json.dumps({"foo": "bar"})
        moesif = MoesifLogger(moesif_options)
        self.assertFalse(moesif.is_base64_str(self=moesif, data=invalid_base64))


class TestProcessBody(unittest.TestCase):
    def test_request_with_valid_base64_body(self):
        """
        Tests that `process_body` successfully processes body from an event.
        `event.body` for this test is a valid
        base64-encoded string: `"eyJ0ZXN0IjoiYm9keSJ9"`.
        """
        with open("moesif_aws_lambda/tests/event_body_valid.json") as event:
            event_payload = json.load(event)
        Moesif = MoesifLogger(moesif_options)
        moesif_middleware = Moesif(lambda_handler)
        _ = moesif_middleware(event_payload, {})
        req_body, transfer_encoding = moesif_middleware.process_body(event_payload)

        self.assertEqual(req_body, "eyJ0ZXN0IjoiYm9keSJ9")
        self.assertEqual(transfer_encoding, "base64")

    def test_request_with_invalid_base64_body_types(self):
        """
        Tests that `process_body` successfully processes body from events
        containing invalid body types.
        `event.body` in these tests are not base64-encoded despite
        `isBase64Encoded` being `true`.
        """
        test_files = [
            "moesif_aws_lambda/tests/event_body_dict.json",
            "moesif_aws_lambda/tests/event_body_int.json",
            "moesif_aws_lambda/tests/event_body_json.json",
        ]

        expected = [
            ({"foo": "bar"}, "json"),
            ("MTA=", "base64"),
            ({"foo": "bar"}, "json"),
        ]

        for i, file in enumerate(test_files):
            with open(file) as event:
                payload = json.load(event)
            moesif = MoesifLogger(moesif_options)
            moesif_middleware = moesif(lambda_handler)
            _ = moesif_middleware(payload, {})

            req_body, transfer_encoding = moesif_middleware.process_body(payload)
            self.assertTupleEqual((req_body, transfer_encoding), expected[i])

    def test_response_with_json_body(self):
        """
        Tests that `process_body` successfully processes response body.
        Body for this test is a valid JSON.
        """
        with open("moesif_aws_lambda/tests/lambda_response.json") as event:
            response_payload = json.load(event)
        Moesif = MoesifLogger(moesif_options)
        moesif_middleware = Moesif(lambda_handler)
        res_body, transfer_encoding = moesif_middleware.process_body(response_payload)

        expected_body = {"message": "Hello from Lambda!"}

        self.assertDictEqual(res_body, expected_body)
        self.assertEqual(transfer_encoding, "json")

    def test_response_with_b64_body(self):
        """
        Tests that `process_body` successfully processes response body.
        Body for this test is binary data encoded in base64.
        """

        response_payload = {
            "statusCode": 200,
            "isBase64Encoded": True,
            "body": "eyJmb28iOiAiYmFyIn0=",
            "headers": {"Content-Type": "application/json"}, 
        }
        
        Moesif = MoesifLogger(moesif_options)
        moesif_middleware = Moesif(lambda_handler)

        res_body, transfer_encoding = moesif_middleware.process_body(response_payload)

        self.assertEqual(res_body, "eyJmb28iOiAiYmFyIn0=")
        self.assertEqual(transfer_encoding, "base64")

if __name__ == "__main__":
    unittest.main()
