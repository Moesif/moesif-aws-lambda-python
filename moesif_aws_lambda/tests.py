import json
import unittest
from .middleware import MoesifLogger

moesif_options = {
    "LOG_BODY": True,
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


if __name__ == "__main__":
    unittest.main()
