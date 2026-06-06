"""Frontend panel registration for ZHA Advanced Toolkit."""

from __future__ import annotations

import logging
from pathlib import Path

from aiohttp import web

from homeassistant.components.frontend import (
    async_panel_exists,
    async_register_built_in_panel,
    async_remove_panel,
)
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    PANEL_JS,
    PANEL_STATIC_REGISTERED,
    PANEL_STATIC_URL,
    PANEL_URL,
    VERSION,
)

_LOGGER = logging.getLogger(__name__)


class ZHAToolkitFrontendView(HomeAssistantView):
    """Serve the toolkit frontend module."""

    requires_auth = False
    url = f"{PANEL_STATIC_URL}/{{filename}}"
    name = f"api:{DOMAIN}:frontend"

    def __init__(self, panel_dir: Path) -> None:
        """Initialize the frontend view."""
        self._panel_dir = panel_dir

    async def get(self, request: web.Request, filename: str) -> web.StreamResponse:
        """Return the requested frontend asset."""
        if filename != PANEL_JS:
            return web.Response(status=404)

        js_file = self._panel_dir / PANEL_JS
        if not js_file.is_file():
            _LOGGER.error("Panel JS is missing at %s", js_file)
            return web.Response(status=404)

        return web.FileResponse(
            js_file,
            headers={
                "Cache-Control": "no-store",
                "Content-Type": "text/javascript; charset=utf-8",
            },
        )


async def async_register_toolkit_panel(hass: HomeAssistant) -> None:
    """Register the toolkit configuration panel."""
    if async_panel_exists(hass, PANEL_URL):
        async_remove_panel(hass, PANEL_URL)

    if not hass.data.get(PANEL_STATIC_REGISTERED):
        panel_dir = Path(__file__).parent / "frontend"
        js_file = panel_dir / PANEL_JS
        _LOGGER.info(
            "Registering ZHA Advanced Toolkit frontend at %s/%s?v=%s "
            "(exists=%s)",
            PANEL_STATIC_URL,
            PANEL_JS,
            VERSION,
            js_file.is_file(),
        )
        hass.http.register_view(ZHAToolkitFrontendView(panel_dir))
        hass.data[PANEL_STATIC_REGISTERED] = True
    async_register_built_in_panel(
        hass,
        component_name="custom",
        frontend_url_path=PANEL_URL,
        config={
            "_panel_custom": {
                "name": "zha-advanced-toolkit-panel",
                "embed_iframe": False,
                "trust_external": False,
                "module_url": f"{PANEL_STATIC_URL}/{PANEL_JS}?v={VERSION}",
            }
        },
        require_admin=True,
        config_panel_domain=DOMAIN,
        show_in_sidebar=False,
    )


def async_remove_toolkit_panel(hass: HomeAssistant) -> None:
    """Remove the toolkit configuration panel."""
    if async_panel_exists(hass, PANEL_URL):
        async_remove_panel(hass, PANEL_URL)
