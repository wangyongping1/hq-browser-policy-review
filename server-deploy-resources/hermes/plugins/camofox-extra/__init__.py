"""camofox-extra plugin: CamoFox-specific helper tools."""

from __future__ import annotations

from . import schemas, tools

_TOOLS = (
    ("camofox_health", schemas.CAMOFOX_HEALTH_SCHEMA, tools.camofox_health),
    ("camofox_tabs", schemas.CAMOFOX_TABS_SCHEMA, tools.camofox_tabs),
    ("camofox_links", schemas.CAMOFOX_LINKS_SCHEMA, tools.camofox_links),
    ("camofox_images", schemas.CAMOFOX_IMAGES_SCHEMA, tools.camofox_images),
    ("camofox_downloads", schemas.CAMOFOX_DOWNLOADS_SCHEMA, tools.camofox_downloads),
    ("camofox_stats", schemas.CAMOFOX_STATS_SCHEMA, tools.camofox_stats),
    ("camofox_screenshot", schemas.CAMOFOX_SCREENSHOT_SCHEMA, tools.camofox_screenshot),
    ("camofox_viewport", schemas.CAMOFOX_VIEWPORT_SCHEMA, tools.camofox_viewport),
    ("camofox_macro_search", schemas.CAMOFOX_MACRO_SEARCH_SCHEMA, tools.camofox_macro_search),
    ("camofox_extract", schemas.CAMOFOX_EXTRACT_SCHEMA, tools.camofox_extract),
)


def _check_camofox_available() -> bool:
    try:
        data = tools._request("GET", "/health", timeout=5)
        return bool(isinstance(data, dict) and data.get("ok"))
    except Exception:
        return False


def register(ctx) -> None:
    for name, schema, handler in _TOOLS:
        ctx.register_tool(
            name=name,
            toolset="camofox_extra",
            schema=schema,
            handler=handler,
            check_fn=_check_camofox_available,
        )
