import json
import urllib.error
import urllib.request
from typing import Any

from minimatic.core import Expression, Symbol
from minimatic.eval.context import EvaluationContext

from .registry import register_builtin

Request = Symbol("Request")


@register_builtin(Request, auto_evaluate=True)
def request_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    Performs a REST API request using only Python standard libraries.

    Usage:
        Request["GET", url]
        Request["GET", url, None, headers]
        Request["POST", url, data_dict]
        Request["POST", url, data_dict, headers_dict]

    Returns a dict with 'status' and 'body' keys on success,
    or 'status', 'error', and 'body' on HTTP errors.
    """
    args = list(expr.args)

    if len(args) < 2:
        return {"error": "Request requires at least 2 arguments: method and url"}

    method = str(args[0]).upper()
    url = str(args[1])
    data = args[2] if len(args) > 2 else None
    headers = args[3] if len(args) > 3 else None

    headers = headers if isinstance(headers, dict) else {}
    encoded_data = None

    if data is not None:
        json_payload = json.dumps(data) if isinstance(data, dict) else str(data)
        encoded_data = json_payload.encode("utf-8")

        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        url=url,
        data=encoded_data,
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            raw_response = response.read().decode("utf-8")

            try:
                parsed_response = json.loads(raw_response)
            except json.JSONDecodeError:
                parsed_response = raw_response

            return {
                "status": status_code,
                "body": parsed_response,
            }

    except urllib.error.HTTPError as e:
        return {
            "status": e.code,
            "error": e.reason,
            "body": e.read().decode("utf-8"),
        }

    except urllib.error.URLError as e:
        return {"error": str(e.reason)}
