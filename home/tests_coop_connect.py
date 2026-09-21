import os
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from .coop_connect import CoopConnectSITClient


class CoopConnectSITClientTests(SimpleTestCase):
    def test_token_generation_uses_basic_auth_and_redacts_token(self):
        session = Mock()
        response = Mock(status_code=200)
        response.json.return_value = {
            "access_token": "secret-token",
            "token_type": "Bearer",
            "expires_in": 600,
        }
        session.request.return_value = response

        with patch.dict(
            os.environ,
            {
                "COOP_CONNECT_SIT_BASE_URL": "https://openapi-sit.co-opbank.co.ke",
                "COOP_CONNECT_SIT_CLIENT_ID": "sit-client",
                "COOP_CONNECT_SIT_CLIENT_SECRET": "sit-secret",
            },
            clear=False,
        ):
            result = CoopConnectSITClient(session=session).generate_token()

        self.assertEqual(result["access_token"], "secret-token")
        self.assertEqual(result["raw"]["access_token"], "[REDACTED]")
        request_kwargs = session.request.call_args.kwargs
        self.assertEqual(request_kwargs["data"], {"grant_type": "client_credentials"})
        self.assertTrue(request_kwargs["headers"]["Authorization"].startswith("Basic "))

    def test_stk_payload_matches_supplied_sit_collection_shape(self):
        session = Mock()
        token_response = Mock(status_code=200)
        token_response.json.return_value = {"access_token": "token"}
        stk_response = Mock(status_code=200)
        stk_response.json.return_value = {"MessageReference": "SHOPIVA-SIT-TEST", "Status": "Accepted"}
        session.request.side_effect = [token_response, stk_response]

        env = {
            "COOP_CONNECT_SIT_BASE_URL": "https://openapi-sit.co-opbank.co.ke",
            "COOP_CONNECT_SIT_CLIENT_ID": "sit-client",
            "COOP_CONNECT_SIT_CLIENT_SECRET": "sit-secret",
            "COOP_CONNECT_SIT_USER_ID": "EntityName",
            "COOP_CONNECT_SIT_OPERATOR_CODE": "001",
        }
        with patch.dict(os.environ, env, clear=False):
            result = CoopConnectSITClient(session=session).stk_push(
                mobile_number="0707919065",
                amount="1",
                callback_url="https://shopivakenya.top/payments/coop-connect/sit/callback/",
                message_reference="SHOPIVA-SIT-TEST",
            )

        sent = session.request.call_args_list[-1].kwargs["json"]
        self.assertEqual(result["message_reference"], "SHOPIVA-SIT-TEST")
        self.assertEqual(sent["MessageReference"], "SHOPIVA-SIT-TEST")
        self.assertEqual(sent["UserId"], "EntityName")
        self.assertEqual(
            sent["CallBackUrl"],
            "https://shopivakenya.top/payments/coop-connect/sit/callback/",
        )
        self.assertEqual(sent["OperatorCode"], "001")
        self.assertEqual(sent["TransactionCurrency"], "KES")
        self.assertEqual(sent["MobileNumber"], "254707919065")
        self.assertEqual(sent["Amount"], 1.0)

    def test_non_https_callback_is_rejected(self):
        with self.assertRaises(ValueError):
            CoopConnectSITClient().stk_push(
                mobile_number="0707919065",
                amount="1",
                callback_url="http://example.invalid/callback",
            )
