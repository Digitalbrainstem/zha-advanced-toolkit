"""Frontend panel registration for ZHA Advanced Toolkit."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.frontend import async_panel_exists, async_remove_panel
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.panel_custom import async_register_panel
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    PANEL_JS,
    PANEL_STATIC_REGISTERED,
    PANEL_STATIC_URL,
    PANEL_URL,
)


async def async_register_toolkit_panel(hass: HomeAssistant) -> None:
    """Register the toolkit configuration panel."""
    if async_panel_exists(hass, PANEL_URL):
        async_remove_panel(hass, PANEL_URL)

    if not hass.data.get(PANEL_STATIC_REGISTERED):
        panel_dir = Path(__file__).parent / "frontend"
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    PANEL_STATIC_URL,
                    str(panel_dir),
                    cache_headers=True,
                )
            ]
        )
        hass.data[PANEL_STATIC_REGISTERED] = True
    await async_register_panel(
        hass,
        frontend_url_path=PANEL_URL,
        webcomponent_name="zha-advanced-toolkit-panel",
        sidebar_title="ZHA Toolkit",
        sidebar_icon="mdi:zigbee",
        module_url=f"{PANEL_STATIC_URL}/{PANEL_JS}",
        require_admin=True,
        config_panel_domain=DOMAIN,
    )


def async_remove_toolkit_panel(hass: HomeAssistant) -> None:
    """Remove the toolkit configuration panel."""
    if async_panel_exists(hass, PANEL_URL):
        async_remove_panel(hass, PANEL_URL)
