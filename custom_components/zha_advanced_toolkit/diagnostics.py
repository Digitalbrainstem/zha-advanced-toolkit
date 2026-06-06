"""Diagnostics for ZHA Advanced Toolkit."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .models import ToolkitData
from .zha import (
    ZHAAccessError,
    get_device_firmware,
    get_device_ieee,
    get_device_manufacturer,
    get_device_model,
    get_zha_devices,
)


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    diagnostics: dict[str, Any] = {
        "entry": {
            "title": entry.title,
            "version": entry.version,
        },
        "toolkit_devices": [],
        "zha_devices": [],
    }

    data: ToolkitData | None = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if data is not None:
        diagnostics["toolkit_devices"] = [
            {
                "ieee": device.ieee,
                "manufacturer": device.manufacturer,
                "model": device.model,
                "firmware": device.firmware,
                "profile": device.profile_name,
                "settings": [setting.key for setting in device.settings],
                "commands": [command.key for command in device.commands],
            }
            for device in data.devices
        ]

    try:
        zha_devices = get_zha_devices(hass)
    except ZHAAccessError as err:
        diagnostics["zha_error"] = str(err)
    else:
        diagnostics["zha_devices"] = [
            {
                "ieee": get_device_ieee(device),
                "manufacturer": get_device_manufacturer(device),
                "model": get_device_model(device),
                "firmware": get_device_firmware(device),
            }
            for device in zha_devices
        ]

    return diagnostics
