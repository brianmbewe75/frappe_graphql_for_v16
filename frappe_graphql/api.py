from graphql import GraphQLError, validate, parse
from typing import List

import frappe
from frappe import _
from frappe.utils import cint, strip_html_tags

# Import workaround for namespace package issue
import sys
import os
_frappe_graphql_path = os.path.join(os.path.dirname(__file__))
if _frappe_graphql_path not in sys.path:
    sys.path.insert(0, _frappe_graphql_path)

from frappe_graphql.utils.loader import get_schema
from graphql import execute as graphql_execute
from graphql_sync_dataloaders import DeferredExecutionContext
from .utils.depth_limit_validator import depth_limit_validator

from .utils.http import get_masked_variables, get_operation_name

def execute(query=None, variables=None, operation_name=None):
    """Execute GraphQL query"""
    result = graphql_execute(
        schema=get_schema(),
        document=parse(query),
        variable_values=variables,
        operation_name=operation_name if operation_name else None,
        middleware=[frappe.get_attr(cmd) for cmd in frappe.get_hooks("graphql_middlewares")],
        context_value=frappe._dict(),
        execution_context_class=DeferredExecutionContext
    )
    output = frappe._dict()
    for k in ("data", "errors"):
        if not getattr(result, k, None):
            continue
        output[k] = getattr(result, k)
    return output


@frappe.whitelist(allow_guest=True)
def execute_gql_query(**kwargs):
    # EARLY CHECK: Read request body directly before anything else (for raw GraphQL)
    query = None
    variables = None
    operation_name = None
    
    try:
        if hasattr(frappe.local, "request"):
            request = frappe.local.request
            # Try to get body immediately
            body = None
            # Check cached data first
            if hasattr(frappe.local, "_graphql_raw_data") and frappe.local._graphql_raw_data:
                body = frappe.local._graphql_raw_data
            # Try request.get_data
            if not body:
                try:
                    body = request.get_data(as_text=True, cache=True)
                except Exception:
                    pass
            # If we have body and it looks like raw GraphQL, use it
            if body and body.strip():
                body_clean = body.strip().replace("\r\n", "\n").replace("\r", "\n")
                if body_clean.startswith("\ufeff"):
                    body_clean = body_clean[1:].strip()
                if body_clean.startswith(("query", "mutation", "subscription")):
                    query = body_clean
    except Exception:
        pass
    
    # When Postman/GraphQL tab sends {"query": "...", "variables": {}}, Frappe parses it and passes
    # as kwargs. Use kwargs if we don't have query yet.
    if not query:
        query = kwargs.get("query")
        variables = kwargs.get("variables")
        operation_name = kwargs.get("operationName") or kwargs.get("operation_name")
        if query and isinstance(query, str):
            query = query.replace("\r\n", "\n").replace("\r", "\n").strip() or None

    # If we have query but no variables, parse body for variables (e.g. createQuotation needs variables)
    if query and variables is None and hasattr(frappe.local, "request"):
        try:
            request = frappe.local.request
            body = (
                (hasattr(frappe.local, "_request_body_raw") and getattr(frappe.local, "_request_body_raw", None))
                or (hasattr(frappe.local, "_graphql_raw_data") and frappe.local._graphql_raw_data)
                or request.get_data(as_text=True, cache=True)
                or ""
            )
            if body and body.strip().startswith("{"):
                parsed = frappe.parse_json(body)
                if isinstance(parsed, dict):
                    variables = parsed.get("variables")
                    if not operation_name:
                        operation_name = parsed.get("operationName") or parsed.get("operation_name")
        except Exception:
            pass

    # Also check form_dict directly (in case kwargs filtering removed it or it wasn't passed)
    if not query and hasattr(frappe.local, "form_dict"):
        fd = frappe.local.form_dict
        if fd and isinstance(fd, dict) and fd.get("query"):
            query = fd.get("query")
            if isinstance(query, str):
                query = query.replace("\r\n", "\n").replace("\r", "\n").strip() or None
            if not variables:
                variables = fd.get("variables")
            if not operation_name:
                operation_name = fd.get("operationName") or fd.get("operation_name")

    # Fallback: body may be JSON {"query":"..."} or raw GraphQL (query/mutation/subscription). Parse directly.
    if not query and hasattr(frappe.local, "request"):
        try:
            request = frappe.local.request
            body = (
                (hasattr(frappe.local, "_graphql_raw_data") and frappe.local._graphql_raw_data)
                or request.get_data(as_text=True, cache=True)
                or ""
            )
            if body and body.strip():
                body_clean = body.strip().replace("\r\n", "\n").replace("\r", "\n")
                if body_clean.startswith("\ufeff"):
                    body_clean = body_clean[1:].strip()
                # Raw GraphQL (e.g. Postman sends raw mutation with Content-Type: application/json)
                if body_clean.startswith(("query", "mutation", "subscription")):
                    query = body_clean
                # Wrapped JSON
                elif body_clean.startswith("{"):
                    parsed = frappe.parse_json(body)
                    if isinstance(parsed, dict) and parsed.get("query"):
                        query = (parsed.get("query") or "").replace("\r\n", "\n").replace("\r", "\n").strip()
                        variables = variables or parsed.get("variables")
                        operation_name = operation_name or parsed.get("operationName") or parsed.get("operation_name")
        except Exception:
            pass

    if not query:
        query, variables, operation_name = get_query()
    
    # Final fallback: if we still don't have query, try reading request body directly
    if not query:
        try:
            if hasattr(frappe.local, "request"):
                request = frappe.local.request
                # Try multiple ways to get the body
                body = None
                # Method 1: cached raw data
                if hasattr(frappe.local, "_graphql_raw_data") and frappe.local._graphql_raw_data:
                    body = frappe.local._graphql_raw_data
                # Method 2: request.get_data
                if not body:
                    try:
                        body = request.get_data(as_text=True, cache=True)
                    except Exception:
                        pass
                # Method 3: input stream
                if not body and hasattr(request, 'input_stream') and request.input_stream:
                    try:
                        request.input_stream.seek(0)
                        body = request.input_stream.read().decode('utf-8')
                        request.input_stream.seek(0)
                    except Exception:
                        pass
                # Method 4: WSGI environ
                if not body and hasattr(request, 'environ') and 'wsgi.input' in request.environ:
                    try:
                        wsgi_input = request.environ['wsgi.input']
                        if hasattr(wsgi_input, 'read'):
                            pos = getattr(wsgi_input, 'tell', lambda: 0)()
                            wsgi_input.seek(0)
                            body = wsgi_input.read().decode('utf-8')
                            wsgi_input.seek(pos)
                    except Exception:
                        pass
                
                if body and body.strip():
                    body_clean = body.strip().replace("\r\n", "\n").replace("\r", "\n")
                    # Remove BOM if present
                    if body_clean.startswith("\ufeff"):
                        body_clean = body_clean[1:].strip()
                    # Check if it's raw GraphQL (query/mutation/subscription)
                    if body_clean.startswith(("query", "mutation", "subscription")):
                        query = body_clean
                        variables = None
                        operation_name = None
                    # Also check if it's wrapped JSON that wasn't parsed
                    elif body_clean.startswith("{") and ("query" in body_clean or "mutation" in body_clean):
                        try:
                            parsed = frappe.parse_json(body_clean)
                            if isinstance(parsed, dict) and parsed.get("query"):
                                query = parsed.get("query")
                                if isinstance(query, str):
                                    query = query.replace("\r\n", "\n").replace("\r", "\n").strip()
                                variables = parsed.get("variables")
                                operation_name = parsed.get("operationName")
                        except Exception:
                            pass
        except Exception:
            pass
    
    if not query:
        frappe.throw(_("GraphQL query is required. Please send your query as raw GraphQL syntax or wrapped in JSON: {\"query\": \"...\"}"), frappe.ValidationError)
    validation_errors = validate(
        schema=get_schema(),
        document_ast=parse(query),
        rules=(
            depth_limit_validator(
                max_depth=cint(frappe.local.conf.get("frappe_graphql_depth_limit")) or 10
            ),
        )
    )
    if validation_errors:
        output = frappe._dict(errors=validation_errors)
    else:
        output = execute(
            query=query,
            variables=variables,
            operation_name=operation_name
        )

    frappe.clear_messages()
    frappe.local.response = output
    if len(output.get("errors", [])):
        frappe.db.rollback()
        log_error(query, variables, operation_name, output)
        frappe.local.response["http_status_code"] = get_max_http_status_code(output.get("errors"))
        errors = []
        for err in output.errors:
            if isinstance(err, GraphQLError):
                err = err.formatted
                err['message'] = strip_html_tags(err.get("message"))
            errors.append(err)
        output.errors = errors


def get_query():
    """
    Gets Query details as per the specs in https://graphql.org/learn/serving-over-http/
    """

    query = None
    variables = None
    operation_name = None
    if not hasattr(frappe.local, "request"):
        return query, variables, operation_name

    # Priority 1: Check cached raw GraphQL data (from make_form_dict when raw GraphQL is sent)
    if hasattr(frappe.local, "_graphql_raw_data") and frappe.local._graphql_raw_data:
        raw = frappe.local._graphql_raw_data.strip()
        if raw.startswith(("query", "mutation", "subscription")):
            query = raw.replace("\r\n", "\n").replace("\r", "\n").strip()
            if query:
                return query, None, None

    # Priority 2: When Content-Type is application/json and body is valid JSON, Frappe parses it into form_dict.
    # Postman "GraphQL" mode sends: {"query": "mutation {...}", "variables": {}} - use it directly.
    # Note: form_dict might be {} (empty dict) when raw GraphQL is sent, so check if it exists and has query key
    if hasattr(frappe.local, "form_dict"):
        fd = frappe.local.form_dict
        if fd and isinstance(fd, dict) and fd.get("query"):
            query = fd.get("query")
            if isinstance(query, str):
                # Normalize \r\n to \n (e.g. from Postman/curl)
                query = query.replace("\r\n", "\n").replace("\r", "\n").strip()
            variables = fd.get("variables")
            operation_name = fd.get("operationName") or fd.get("operation_name")
            if query:
                return query, variables, operation_name

    from werkzeug.wrappers import Request
    request: Request = frappe.local.request
    content_type = request.content_type or ""

    if request.method == "GET":
        query = frappe.safe_decode(request.args["query"])
        variables = frappe.safe_decode(request.args["variables"])
        operation_name = frappe.safe_decode(request.args["operation_name"])
    elif request.method == "POST":
        # Collect all possible sources of request data
        request_data = None
        
        # 1. Check cached data from make_form_dict (most reliable for raw GraphQL)
        if hasattr(frappe.local, "_graphql_raw_data") and frappe.local._graphql_raw_data:
            request_data = frappe.local._graphql_raw_data
        
        # 2. Try to get from request (use cache=True to allow multiple reads)
        if not request_data or not request_data.strip():
            try:
                request_data = request.get_data(as_text=True, cache=True)
            except Exception:
                request_data = None
        
        # 3. Try reading from input stream if available
        if not request_data or not request_data.strip():
            try:
                if hasattr(request, 'input_stream') and request.input_stream:
                    request.input_stream.seek(0)
                    request_data = request.input_stream.read().decode('utf-8')
                    request.input_stream.seek(0)  # Reset for potential future reads
            except Exception:
                pass
        
        # 4. Last resort: try to get from request.environ (raw WSGI input)
        if not request_data or not request_data.strip():
            try:
                if hasattr(request, 'environ') and 'wsgi.input' in request.environ:
                    wsgi_input = request.environ['wsgi.input']
                    if hasattr(wsgi_input, 'read'):
                        # Save current position
                        pos = getattr(wsgi_input, 'tell', lambda: 0)()
                        wsgi_input.seek(0)
                        request_data = wsgi_input.read().decode('utf-8')
                        wsgi_input.seek(pos)  # Restore position
            except Exception:
                pass
        
        # Support application/graphql content type (raw GraphQL syntax)
        if "application/graphql" in content_type:
            if request_data and request_data.strip():
                query = request_data.strip()
        
        # Support application/json with wrapped format {"query": "..."} or raw GraphQL
        elif "application/json" in content_type:
            # If request_data is empty, check cached data first (from make_form_dict)
            # This is critical for Postman/API tools where data might be consumed
            if not request_data or not request_data.strip():
                if hasattr(frappe.local, "_graphql_raw_data") and frappe.local._graphql_raw_data:
                    request_data = frappe.local._graphql_raw_data
            
            if request_data and request_data.strip():
                # First, check if it's raw GraphQL syntax (starts with query/mutation/subscription)
                request_data_stripped = request_data.strip()
                if request_data_stripped.startswith(("query", "mutation", "subscription")):
                    # It's raw GraphQL - use it directly
                    query = request_data_stripped
                else:
                    # Try to parse as JSON (wrapped format)
                    try:
                        graphql_request = frappe.parse_json(request_data)
                        # Check if it's the wrapped format
                        if isinstance(graphql_request, dict) and "query" in graphql_request:
                            query = graphql_request.get("query")
                            variables = graphql_request.get("variables")
                            operation_name = graphql_request.get("operationName")
                        elif isinstance(graphql_request, str):
                            # Raw GraphQL sent as JSON string
                            query = graphql_request.strip()
                    except (ValueError, TypeError, Exception):
                        # JSON parsing failed - might be raw GraphQL with special characters
                        # Try treating as raw GraphQL anyway
                        if request_data_stripped.startswith(("query", "mutation", "subscription")):
                            query = request_data_stripped
        
        # Support raw GraphQL when Content-Type is text/plain or not specified but body looks like GraphQL
        elif "text/plain" in content_type or (not content_type and request_data and request_data.strip().startswith(("query", "mutation", "subscription"))):
            if request_data and request_data.strip():
                query = request_data.strip()
        
        elif "multipart/form-data" in content_type:
            # Follows the spec here: https://github.com/jaydenseric/graphql-multipart-request-spec
            # This could be used for file uploads, single / multiple
            operations = frappe.parse_json(request.form.get("operations"))
            query = operations.get("query")
            variables = operations.get("variables")
            operation_name = operations.get("operationName")

            files_map = frappe.parse_json(request.form.get("map"))
            for file_key in files_map:
                file_instances = files_map[file_key]
                for file_instance in file_instances:
                    path = file_instance.split(".")
                    obj = operations[path.pop(0)]
                    while len(path) > 1:
                        obj = obj[path.pop(0)]

                    obj[path.pop(0)] = file_key

        # Fallback: body looks like raw GraphQL (e.g. mutation { ... }) regardless of Content-Type
        if not query and request_data and request_data.strip():
            raw = request_data.strip()
            if raw.startswith("\ufeff"):
                raw = raw[1:].strip()
            raw = raw.replace("\r\n", "\n").replace("\r", "\n")
            if raw.startswith(("query", "mutation", "subscription")):
                query = raw

    # Normalize query for parser (line endings, BOM)
    if query and isinstance(query, str):
        query = query.replace("\r\n", "\n").replace("\r", "\n").strip()
        if query.startswith("\ufeff"):
            query = query[1:].strip()

    return query, variables, operation_name


def get_max_http_status_code(errors: List[GraphQLError]):
    http_status_code = 400
    for error in errors:
        exc = error.original_error

        if not exc:
            continue

        exc_status = getattr(exc, "http_status_code", 400)
        if exc_status > http_status_code:
            http_status_code = exc_status

    return http_status_code


def log_error(query, variables, operation_name, output):
    import traceback as tb
    tracebacks = []
    for idx, err in enumerate(output.errors):
        if not isinstance(err, GraphQLError):
            continue

        exc = err.original_error
        if not exc:
            continue
        tracebacks.append(
            f"GQLError #{idx}\n"
            + f"Http Status Code: {getattr(exc, 'http_status_code', 500)}\n"
            + f"{str(err)}\n\n"
            + f"{''.join(tb.format_exception(exc, exc, exc.__traceback__))}"
        )

    tracebacks.append(f"Frappe Traceback: \n{frappe.get_traceback()}")
    if frappe.conf.get("developer_mode"):
        frappe.errprint(tracebacks)

    tracebacks = "\n==========================================\n".join(tracebacks)
    if frappe.conf.get("developer_mode"):
        print(tracebacks)
    # Try to log error, but don't fail if GraphQL Error Log DocType doesn't exist
    try:
        if frappe.db.exists("DocType", "GraphQL Error Log"):
            error_log = frappe.new_doc("GraphQL Error Log")
            error_log.update(frappe._dict(
                title="GraphQL API Error",
                operation_name=get_operation_name(query, operation_name),
                query=query,
                variables=frappe.as_json(get_masked_variables(query, variables)) if variables else None,
                output=frappe.as_json(output),
                traceback=tracebacks
            ))
            error_log.insert(ignore_permissions=True)
    except Exception:
        # Silently fail if error logging isn't available
        pass
        pass