"""CamoFox REST API helper tools for Hermes."""

from __future__ import annotations

import json
import os
import uuid
from typing import Any, Dict, Optional

import requests

from tools.registry import tool_error, tool_result

DEFAULT_CAMOFOX_URL = "http://camofox-browser:9377"
DEFAULT_TIMEOUT = 30


def _base_url() -> str:
    return os.getenv("CAMOFOX_URL", DEFAULT_CAMOFOX_URL).rstrip("/")


def _headers() -> Dict[str, str]:
    headers = {"Content-Type": "application/json"}
    api_key = os.getenv("CAMOFOX_API_KEY", "").strip()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _request(method: str, path: str, *, params: Optional[dict] = None, body: Optional[dict] = None, timeout: int = DEFAULT_TIMEOUT) -> Any:
    url = f"{_base_url()}{path}"
    try:
        resp = requests.request(method, url, params=params, json=body, headers=_headers(), timeout=timeout)
        if resp.status_code >= 400:
            return {"success": False, "status_code": resp.status_code, "error": resp.text[:1000]}
        if not resp.content:
            return {"success": True}
        try:
            return resp.json()
        except ValueError:
            return {"success": True, "text": resp.text}
    except Exception as exc:
        return {"success": False, "error": f"{type(exc).__name__}: {exc}"}


def _request_raw(method: str, path: str, *, params: Optional[dict] = None, body: Optional[dict] = None, timeout: int = DEFAULT_TIMEOUT) -> Any:
    url = f"{_base_url()}{path}"
    try:
        resp = requests.request(method, url, params=params, json=body, headers=_headers(), timeout=timeout)
        if resp.status_code >= 400:
            return {"success": False, "status_code": resp.status_code, "error": resp.text[:1000]}
        return resp
    except Exception as exc:
        return {"success": False, "error": f"{type(exc).__name__}: {exc}"}


def _screenshot_dir() -> str:
    try:
        from hermes_constants import get_hermes_home  # type: ignore
        path = get_hermes_home() / "browser_screenshots"
    except Exception:
        path = os.path.join("/tmp", "camofox_screenshots")
    os.makedirs(path, exist_ok=True)
    return str(path)


def _current_tab(task_id: Optional[str], tab_id: Optional[str] = None) -> tuple[Optional[str], Optional[str], Optional[str]]:
    if tab_id:
        try:
            from tools.browser_camofox import _get_session  # type: ignore
            session = _get_session(task_id or "default")
            return tab_id, session.get("user_id"), None
        except Exception:
            return tab_id, "test", None
    try:
        from tools.browser_camofox import _get_session  # type: ignore
        session = _get_session(task_id or "default")
    except Exception as exc:
        return None, None, f"CamoFox session lookup failed: {exc}"
    current = session.get("tab_id")
    if not current:
        return None, session.get("user_id"), "No current CamoFox tab. Call browser_navigate first, then use camofox_* helper tools."
    return current, session.get("user_id"), None


def _limit(raw: Any, default: int = 50) -> int:
    try:
        value = int(raw)
    except Exception:
        value = default
    return max(1, min(200, value))


def _offset(raw: Any) -> int:
    try:
        value = int(raw)
    except Exception:
        value = 0
    return max(0, value)


def _with_tab(args: dict, task_id: Optional[str]) -> tuple[Optional[str], Optional[str], Optional[str]]:
    return _current_tab(task_id, args.get("tab_id") or None)


def _as_result(data: Any) -> str:
    if isinstance(data, dict) and data.get("success") is False:
        return tool_error(data.get("error", "CamoFox request failed"), status_code=data.get("status_code"))
    return tool_result(data)


def _extract_schema_input(args: dict) -> Any:
    raw = args.get("schema")
    if raw is None and args.get("schema_json"):
        raw = args.get("schema_json")
    if raw is None and isinstance(args.get("fields"), dict):
        raw = {"type": "object", "properties": args.get("fields"), "required": args.get("required")}
    if raw is None and isinstance(args.get("properties"), dict):
        raw = {"type": "object", "properties": args.get("properties"), "required": args.get("required")}
    return raw


def _normalize_extract_schema(raw: Any) -> tuple[Optional[dict], Optional[str]]:
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception as exc:
            return None, f"schema_json must be valid JSON: {exc}"

    if not isinstance(raw, dict):
        return None, "schema must be a JSON object, schema_json string, or fields object"

    schema = dict(raw)

    # Some tool-call serializers are fragile around nested JSON Schema keys.
    # Accept wrappers and shorthands so callers can avoid passing a nested `type` key.
    if isinstance(schema.get("schema"), dict) and "properties" not in schema:
        schema = dict(schema["schema"])
    if "fields" in schema and "properties" not in schema and isinstance(schema["fields"], dict):
        schema = {"type": "object", "properties": schema["fields"], "required": schema.get("required")}
    if "properties" not in schema and any(k not in {"type", "required", "description", "$schema"} for k in schema):
        schema = {"type": "object", "properties": schema, "required": schema.get("required")}

    schema["type"] = "object"

    props = schema.get("properties")
    if not isinstance(props, dict) or not props:
        return None, "schema.properties must be a non-empty object"

    normalized_props = {}
    for name, spec in props.items():
        field_name = str(name).strip()
        if not field_name:
            continue
        if isinstance(spec, str):
            spec_obj = {"type": spec}
        elif isinstance(spec, dict):
            spec_obj = dict(spec)
        else:
            spec_obj = {"type": "string"}

        field_type = spec_obj.get("type")
        if isinstance(field_type, list):
            field_type = next((t for t in field_type if t != "null"), field_type[0] if field_type else "string")
        if not field_type:
            field_type = "string"
        elif field_type == "array":
            field_type = "object"
            spec_obj.setdefault("description", "Array-like data; use camofox_links or camofox_images for native lists.")
        elif field_type not in {"string", "number", "integer", "boolean", "object", "null"}:
            field_type = "string"
        spec_obj["type"] = field_type
        normalized_props[field_name] = spec_obj

    if not normalized_props:
        return None, "schema.properties must contain at least one field"

    schema["properties"] = normalized_props
    required = schema.get("required")
    if required is not None:
        if not isinstance(required, list):
            schema["required"] = []
        else:
            schema["required"] = [str(x) for x in required if str(x) in normalized_props]
    return schema, None


def camofox_health(args: dict, **kw) -> str:
    return _as_result(_request("GET", "/health", timeout=10))


def camofox_tabs(args: dict, **kw) -> str:
    return _as_result(_request("GET", "/tabs", timeout=10))


def camofox_links(args: dict, **kw) -> str:
    tab_id, user_id, err = _with_tab(args, kw.get("task_id"))
    if err:
        return tool_error(err)
    params = {"userId": user_id, "offset": _offset(args.get("offset")), "limit": _limit(args.get("limit"))}
    return _as_result(_request("GET", f"/tabs/{tab_id}/links", params=params))


def camofox_images(args: dict, **kw) -> str:
    tab_id, user_id, err = _with_tab(args, kw.get("task_id"))
    if err:
        return tool_error(err)
    params = {"userId": user_id, "offset": _offset(args.get("offset")), "limit": _limit(args.get("limit"))}
    return _as_result(_request("GET", f"/tabs/{tab_id}/images", params=params))


def camofox_downloads(args: dict, **kw) -> str:
    tab_id, user_id, err = _with_tab(args, kw.get("task_id"))
    if err:
        return tool_error(err)
    return _as_result(_request("GET", f"/tabs/{tab_id}/downloads", params={"userId": user_id}))


def camofox_stats(args: dict, **kw) -> str:
    tab_id, user_id, err = _with_tab(args, kw.get("task_id"))
    if err:
        return tool_error(err)
    return _as_result(_request("GET", f"/tabs/{tab_id}/stats", params={"userId": user_id}))


def camofox_screenshot(args: dict, **kw) -> str:
    tab_id, user_id, err = _with_tab(args, kw.get("task_id"))
    if err:
        return tool_error(err)
    resp = _request_raw("GET", f"/tabs/{tab_id}/screenshot", params={"userId": user_id}, timeout=60)
    if isinstance(resp, dict) and resp.get("success") is False:
        return tool_error(resp.get("error", "CamoFox screenshot request failed"), status_code=resp.get("status_code"))

    content_type = resp.headers.get("content-type", "image/png")
    ext = ".png" if "png" in content_type.lower() else ".bin"
    screenshot_path = os.path.join(_screenshot_dir(), f"camofox_screenshot_{uuid.uuid4().hex[:8]}{ext}")
    with open(screenshot_path, "wb") as f:
        f.write(resp.content)

    return tool_result({
        "success": True,
        "screenshot_path": screenshot_path,
        "content_type": content_type,
        "bytes": len(resp.content),
        "tab_id": tab_id,
    })


def camofox_viewport(args: dict, **kw) -> str:
    tab_id, user_id, err = _with_tab(args, kw.get("task_id"))
    if err:
        return tool_error(err)
    try:
        width = int(args.get("width"))
        height = int(args.get("height"))
    except Exception:
        return tool_error("width and height must be integers")
    if not (100 <= width <= 10000 and 100 <= height <= 10000):
        return tool_error("width and height must be between 100 and 10000")
    return _as_result(_request("POST", f"/tabs/{tab_id}/viewport", body={"userId": user_id, "width": width, "height": height}))


def camofox_macro_search(args: dict, **kw) -> str:
    tab_id, user_id, err = _with_tab(args, kw.get("task_id"))
    if err:
        return tool_error(err)
    macro = str(args.get("macro") or "").strip()
    query = str(args.get("query") or "").strip()
    if not macro.startswith("@") or not query:
        return tool_error("macro must start with @ and query must be non-empty")
    return _as_result(_request("POST", f"/tabs/{tab_id}/navigate", body={"userId": user_id, "macro": macro, "query": query}, timeout=60))


def camofox_extract(args: dict, **kw) -> str:
    tab_id, user_id, err = _with_tab(args, kw.get("task_id"))
    if err:
        return tool_error(err)
    schema, schema_err = _normalize_extract_schema(_extract_schema_input(args))
    if schema_err:
        return tool_error(schema_err)

    payload = {"userId": user_id, "schema": schema}
    data = _request("POST", f"/tabs/{tab_id}/extract", body=payload, timeout=60)
    if isinstance(data, dict) and data.get("status_code") == 409:
        _request("GET", f"/tabs/{tab_id}/snapshot", params={"userId": user_id}, timeout=60)
        data = _request("POST", f"/tabs/{tab_id}/extract", body=payload, timeout=60)
    return _as_result(data)
