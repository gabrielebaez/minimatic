"""Tests for Web builtins module."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

# Force registration of builtins
import minimatic.builtins.io  # noqa: F401
from minimatic.builtins.registry import has_builtin
from minimatic.core.expression import Expression
from minimatic.core.symbol import Symbol
from minimatic.eval.evaluator import evaluate

Request = Symbol("Request")


class TestRequestRegistration:
    def test_request_is_registered(self):
        assert has_builtin(Request)


class TestRequestGet:
    @patch("minimatic.builtins.io.urllib.request.urlopen")
    def test_get_request(self, mock_urlopen, ctx):
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = json.dumps({"key": "value"}).encode("utf-8")
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = evaluate(Expression(Request, "GET", "https://api.example.com/data"), ctx)

        assert result["status"] == 200
        assert result["body"] == {"key": "value"}

    @patch("minimatic.builtins.io.urllib.request.urlopen")
    def test_get_with_headers(self, mock_urlopen, ctx):
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = json.dumps({"headers": {"X-Test": "abc"}}).encode(
            "utf-8"
        )
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = evaluate(
            Expression(
                Request,
                "GET",
                "https://api.example.com/headers",
                None,
                {"X-Test": "abc"},
            ),
            ctx,
        )

        assert result["status"] == 200
        # Verify the request was made with the custom header
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        assert req.get_header("X-test") == "abc"


class TestRequestPost:
    @patch("minimatic.builtins.io.urllib.request.urlopen")
    def test_post_json(self, mock_urlopen, ctx):
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = json.dumps({"received": True}).encode("utf-8")
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        payload = {"message": "hello", "value": 42}
        result = evaluate(
            Expression(Request, "POST", "https://api.example.com/data", payload),
            ctx,
        )

        assert result["status"] == 200
        # Verify JSON content type was set
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        assert req.get_header("Content-type") == "application/json"


class TestRequestErrors:
    @patch("minimatic.builtins.io.urllib.request.urlopen")
    def test_http_error(self, mock_urlopen, ctx):
        import urllib.error

        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://api.example.com/missing",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=MagicMock(read=MagicMock(return_value=b"Not found")),
        )

        result = evaluate(Expression(Request, "GET", "https://api.example.com/missing"), ctx)

        assert result["status"] == 404
        assert result["error"] == "Not Found"

    @patch("minimatic.builtins.io.urllib.request.urlopen")
    def test_url_error(self, mock_urlopen, ctx):
        import urllib.error

        mock_urlopen.side_effect = urllib.error.URLError("DNS resolution failed")

        result = evaluate(
            Expression(Request, "GET", "https://this-does-not-exist.invalid"), ctx
        )

        assert "error" in result
        assert "DNS resolution failed" in result["error"]

    def test_missing_arguments(self, ctx):
        result = evaluate(Expression(Request), ctx)
        assert "error" in result

    def test_missing_url(self, ctx):
        result = evaluate(Expression(Request, "GET"), ctx)
        assert "error" in result
