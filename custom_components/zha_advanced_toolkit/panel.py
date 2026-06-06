"""Frontend panel registration for ZHA Advanced Toolkit."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.frontend import (
    async_panel_exists,
    async_register_built_in_panel,
    async_remove_panel,
)
from homeassistant.core import HomeAssistant

try:
    from homeassistant.components.http import StaticPathConfig
except ImportError:
    StaticPathConfig = None

from .const import (
    DOMAIN,
    PANEL_JS,
    PANEL_STATIC_REGISTERED,
    PANEL_STATIC_URL,
    PANEL_URL,
    VERSION,
)


async def _async_register_static_path(hass: HomeAssistant, panel_dir: Path) -> None:
    """Register the panel static path across HA versions."""
    if StaticPathConfig is not None and hasattr(hass.http, "async_register_static_paths"):
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    PANEL_STATIC_URL,
                    str(panel_dir),
                    cache_headers=False,
                )
            ]
        )
        return

    if hasattr(hass.http, "async_register_static_path"):
        await hass.http.async_register_static_path(
            PANEL_STATIC_URL,
            str(panel_dir),
            False,
        )
        return

    hass.http.register_static_path(PANEL_STATIC_URL, str(panel_dir), False)


async def async_register_toolkit_panel(hass: HomeAssistant) -> None:
    """Register the toolkit configuration panel."""
    if async_panel_exists(hass, PANEL_URL):
        async_remove_panel(hass, PANEL_URL)

    if not hass.data.get(PANEL_STATIC_REGISTERED):
        panel_dir = Path(__file__).parent / "frontend"
        await _async_register_static_path(hass, panel_dir)
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
