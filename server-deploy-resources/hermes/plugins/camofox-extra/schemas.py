"""Tool schemas for the camofox-extra Hermes plugin."""

CAMOFOX_HEALTH_SCHEMA = {
    "name": "camofox_health",
    "description": (
        "Check the CamoFox browser service health and runtime status. "
        "Use for CamoFox-specific diagnostics, not for opening or navigating pages."
    ),
    "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
}

CAMOFOX_TABS_SCHEMA = {
    "name": "camofox_tabs",
    "description": (
        "List CamoFox tabs known to the service. Use for diagnostics only. "
        "Open and navigate normal pages with browser_navigate, not this tool."
    ),
    "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
}

_TAB_ID_FIELD = {
    "type": "string",
    "description": (
        "Optional CamoFox tab id. Leave empty to use the current Hermes browser tab "
        "created by browser_navigate in this conversation."
    ),
}

CAMOFOX_LINKS_SCHEMA = {
    "name": "camofox_links",
    "description": (
        "Extract links from the current CamoFox page. Call browser_navigate first. "
        "This is an enhanced metadata extraction tool, not a navigation tool."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "tab_id": _TAB_ID_FIELD,
            "offset": {"type": "integer", "description": "Pagination offset.", "default": 0},
            "limit": {"type": "integer", "description": "Maximum links to return, 1-200.", "default": 50},
        },
        "additionalProperties": False,
    },
}

CAMOFOX_IMAGES_SCHEMA = {
    "name": "camofox_images",
    "description": (
        "Extract images from the current CamoFox page. Call browser_navigate first. "
        "Use this when browser_get_images is insufficient or CamoFox native image metadata is needed."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "tab_id": _TAB_ID_FIELD,
            "offset": {"type": "integer", "description": "Pagination offset.", "default": 0},
            "limit": {"type": "integer", "description": "Maximum images to return, 1-200.", "default": 50},
        },
        "additionalProperties": False,
    },
}

CAMOFOX_DOWNLOADS_SCHEMA = {
    "name": "camofox_downloads",
    "description": "List downloads associated with the current CamoFox tab. Call browser_navigate first.",
    "parameters": {"type": "object", "properties": {"tab_id": _TAB_ID_FIELD}, "additionalProperties": False},
}

CAMOFOX_STATS_SCHEMA = {
    "name": "camofox_stats",
    "description": "Return CamoFox tab statistics such as URL, visited URLs, ref count, and downloads count. Call browser_navigate first.",
    "parameters": {"type": "object", "properties": {"tab_id": _TAB_ID_FIELD}, "additionalProperties": False},
}

CAMOFOX_SCREENSHOT_SCHEMA = {
    "name": "camofox_screenshot",
    "description": (
        "Save a raw PNG screenshot of the current CamoFox tab and return screenshot_path. "
        "Call browser_navigate first. Use browser_vision instead when the task is to visually analyze the page; "
        "this tool only captures the CamoFox REST screenshot artifact."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "tab_id": _TAB_ID_FIELD,
        },
        "additionalProperties": False,
    },
}

CAMOFOX_VIEWPORT_SCHEMA = {
    "name": "camofox_viewport",
    "description": (
        "Set the viewport size of the current CamoFox tab. Call browser_navigate first. "
        "This changes viewport only; it does not change low-level fingerprint launch options."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "tab_id": _TAB_ID_FIELD,
            "width": {"type": "integer", "description": "Viewport width in CSS pixels.", "default": 1920},
            "height": {"type": "integer", "description": "Viewport height in CSS pixels.", "default": 1080},
        },
        "required": ["width", "height"],
        "additionalProperties": False,
    },
}

CAMOFOX_MACRO_SEARCH_SCHEMA = {
    "name": "camofox_macro_search",
    "description": (
        "Navigate the current CamoFox tab using a built-in CamoFox search macro, such as "
        "@google_search, @youtube_search, @reddit_search, @wikipedia_search, @twitter_search, "
        "@linkedin_search, @instagram_search, @tiktok_search, or @twitch_search. "
        "Use browser_navigate for ordinary URLs and for opening the cloud browser."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "tab_id": _TAB_ID_FIELD,
            "macro": {"type": "string", "description": "CamoFox macro name, for example @google_search or @wikipedia_search."},
            "query": {"type": "string", "description": "Search query for the macro."},
        },
        "required": ["macro", "query"],
        "additionalProperties": False,
    },
}

_EXTRACT_PROPERTY_SCHEMA = {
    "type": "object",
    "description": "One extracted field. CamoFox supports primitive property types and optional x-ref hints.",
    "properties": {
        "type": {
            "type": "string",
            "description": "Field type. Prefer string, number, integer, boolean, object, or null. Use camofox_links for link lists.",
            "enum": ["string", "number", "integer", "boolean", "object", "null"],
        },
        "x-ref": {"type": "string", "description": "Optional snapshot element ref, for example e1."},
    },
    "additionalProperties": True,
}

CAMOFOX_EXTRACT_SCHEMA = {
    "name": "camofox_extract",
    "description": (
        "Run CamoFox structured extraction on the current page. Call browser_navigate first. "
        "Prefer the fields shorthand, for example fields={'title':'string','summary':'string'}, "
        "because some tool-call serializers drop nested JSON Schema type fields. "
        "For page link lists, prefer camofox_links; CamoFox extract is best for scalar fields or x-ref extraction."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "tab_id": _TAB_ID_FIELD,
            "fields": {
                "type": "object",
                "description": "Preferred shorthand. Map field names to primitive types, for example {'title':'string'}.",
                "additionalProperties": {"type": "string", "enum": ["string", "number", "integer", "boolean", "object", "null"]},
            },
            "properties": {
                "type": "object",
                "description": "JSON Schema properties map without the top-level type wrapper.",
                "additionalProperties": _EXTRACT_PROPERTY_SCHEMA,
            },
            "required": {"type": "array", "items": {"type": "string"}},
            "schema_json": {
                "type": "string",
                "description": "Raw JSON string for an object JSON Schema. Use only when fields/properties are insufficient.",
            },
            "schema": {
                "type": "object",
                "description": "Backward-compatible full JSON Schema object. The tool normalizes missing or mangled type fields.",
                "additionalProperties": True,
            },
        },
        "additionalProperties": False,
    },
}
