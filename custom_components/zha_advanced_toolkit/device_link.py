"""Device-page links for ZHA Advanced Toolkit."""

from __future__ import annotations

import logging
from urllib.parse import quote

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import PANEL_URL, ZHA_DOMAIN
from .models import ToolkitDevice

_LOGGER = logging.getLogger(__name__)

TOOLKIT_URL_PREFIX = f"homeassistant://{PANEL_URL}"


def _configuration_url(device: ToolkitDevice) -> str:
    """Return the internal toolkit URL for a device."""
    return f"{TOOLKIT_URL_PREFIX}?ieee={quote(device.ieee)}"


def _registry_device(
    registry: dr.DeviceRegistry,
    device: ToolkitDevice,
) -> dr.DeviceEntry | None:
    """Return the Home Assistant device registry entry for a toolkit device."""
    return registry.async_get_device(
        identifiers={(ZHA_DOMAIN, device.ieee)},
        connections={(dr.CONNECTION_ZIGBEE, device.ieee)},
    )


def async_attach_device_links(
    hass: HomeAssistant,
    devices: list[ToolkitDevice],
) -> None:
    """Attach toolkit configuration links to supported ZHA device pages."""
    registry = dr.async_get(hass)
    for device in devices:
        registry_device = _registry_device(registry, device)
        if registry_device is None:
            _LOGGER.debug("No device registry entry found for %s", device.ieee)
            continue
        current_url = registry_device.configuration_url
        if current_url and not current_url.startswith(TOOLKIT_URL_PREFIX):
            _LOGGER.warning(
                "Not replacing existing configuration URL for %s: %s",
                device.ieee,
                current_url,
            )
            continue
        registry.async_update_device(
            registry_device.id,
            configuration_url=_configuration_url(device),
        )


def async_remove_device_links(
    hass: HomeAssistant,
    devices: list[ToolkitDevice],
) -> None:
    """Remove toolkit configuration links from supported ZHA device pages."""
    registry = dr.async_get(hass)
    for device in devices:
        registry_device = _registry_device(registry, device)
        if registry_device is None:
            continue
        current_url = registry_device.configuration_url
        if current_url and current_url.startswith(TOOLKIT_URL_PREFIX):
            registry.async_update_device(registry_device.id, configuration_url=None)
