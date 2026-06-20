"""
Request Builtin Example
=======================

Demonstrates the Request builtin for making HTTP requests.
Uses httpbin.org as a public test API.
"""

from minimatic import Expression, GlobalContext, evaluate
from minimatic.builtins import Request

ctx = GlobalContext

# --- GET request ---

print("=== GET Request ===")
get_result = evaluate(
    Expression(Request, "GET", "https://httpbin.org/get"),
    ctx,
)
print(f"Status: {get_result['status']}")
if isinstance(get_result["body"], dict):
    print(f"Body origin: {get_result['body'].get('origin', 'N/A')}")
else:
    print(f"Body: {get_result['body'][:100]}...")
print()

# --- GET with custom headers ---

print("=== GET with Custom Headers ===")
get_headers_result = evaluate(
    Expression(
        Request,
        "GET",
        "https://httpbin.org/headers",
        None,
        {"X-Custom-Header": "minimatic-value"},
    ),
    ctx,
)
print(f"Status: {get_headers_result['status']}")
if isinstance(get_headers_result["body"], dict):
    print(f"Headers received: {get_headers_result['body'].get('headers', {})}")
else:
    print(f"Body: {get_headers_result['body'][:100]}...")
print()

# --- POST with JSON body ---

print("=== POST Request ===")
post_result = evaluate(
    Expression(
        Request,
        "POST",
        "https://httpbin.org/post",
        {"message": "Hello from Minimatic!", "value": 42},
    ),
    ctx,
)
print(f"Status: {post_result['status']}")
if isinstance(post_result["body"], dict):
    print(f"JSON received: {post_result['body'].get('json', {})}")
else:
    print(f"Body: {post_result['body'][:100]}...")
print()

# --- Error handling (invalid URL) ---

print("=== Error Handling ===")
error_result = evaluate(
    Expression(Request, "GET", "https://this-domain-does-not-exist.invalid"),
    ctx,
)
print(f"Error: {error_result.get('error', 'N/A')}")
