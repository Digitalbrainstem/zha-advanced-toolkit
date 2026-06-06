"""ZHA Advanced Toolkit integration."""

from __future__ import annotations

import logging

from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, SERVICE_DIAGNOSE
from .models import ToolkitData
from .profiles import get_matching_profile
from .zha import (
    ZHAAccessError,
    get_device_firmware,
    get_device_manufacturer,
    get_device_model,
    get_zha_devices,
)

_LOGGER = logging.getLogger(__name__)
NO_DEVICES_NOTIFICATION_ID = "zha_advanced_toolkit_no_devices"
DIAGNOSTIC_NOTIFICATION_ID = "zha_advanced_toolkit_diagnostics"

PLATFORMS: tuple[Platform, ...] = (
    Platform.SELECT,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.BUTTON,
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ZHA Advanced Toolkit from a config entry."""
    try:
        zha_devices = get_zha_devices(hass)
    except ZHAAccessError as err:
        raise ConfigEntryNotReady(str(err)) from err

    toolkit_data = ToolkitData(devices=[])

    for zha_device in zha_devices:
        manufacturer = get_device_manufacturer(zha_device)
        model = get_device_model(zha_device)
        profile = get_matching_profile(manufacturer, model)
        if profile is None:
            continue

        firmware = get_device_firmware(zha_device)
        settings = [
            setting for setting in profile.settings if setting.supports_firmware(firmware)
        ]
        commands = [
            command for command in profile.commands if command.supports_firmware(firmware)
        ]

        if settings or commands:
            toolkit_data.devices.append(
                profile.create_device(zha_device, settings, commands)
            )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = toolkit_data
    _LOGGER.info(
        "Discovered %d supported ZHA advanced device(s)", len(toolkit_data.devices)
    )
    if not toolkit_data.devices:
        _LOGGER.warning(
            "No supported ZHA advanced devices were discovered from %d ZHA device(s)",
            len(zha_devices),
        )
        detected = ", ".join(
            f"{get_device_manufacturer(device) or 'Unknown'} "
            f"{get_device_model(device) or 'Unknown'}"
            for device in zha_devices
        )
        persistent_notification.async_create(
            hass,
            (
                "ZHA Advanced Toolkit did not find any supported devices. "
                "Confirm the Inovelli device is available in ZHA and that ZHA has "
                "finished starting, then reload this integration."
                f"\n\nDetected ZHA devices: {detected or 'none'}"
            ),
            title="ZHA Advanced Toolkit",
            notification_id=NO_DEVICES_NOTIFICATION_ID,
        )
    else:
        persistent_notification.async_dismiss(hass, NO_DEVICES_NOTIFICATION_ID)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def diagnose_service(_) -> None:
        """Create a notification with current ZHA discovery diagnostics."""
        try:
            devices = get_zha_devices(hass)
        except ZHAAccessError as err:
            message = f"Unable to access ZHA: {err}"
        else:
            lines = [
                (
                    f"- {get_device_manufacturer(device) or 'Unknown'} "
                    f"{get_device_model(device) or 'Unknown'}"
                    f" | firmware={get_device_firmware(device) or 'unknown'}"
                )
                for device in devices
            ]
            message = (
                f"Detected {len(devices)} ZHA device(s):\n"
                + ("\n".join(lines) if lines else "- none")
            )
        persistent_notification.async_create(
            hass,
            message,
            title="ZHA Advanced Toolkit diagnostics",
            notification_id=DIAGNOSTIC_NOTIFICATION_ID,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_DIAGNOSE):
        hass.services.async_register(DOMAIN, SERVICE_DIAGNOSE, diagnose_service)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a ZHA Advanced Toolkit config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        if not hass.data.get(DOMAIN):
            hass.services.async_remove(DOMAIN, SERVICE_DIAGNOSE)
    return unload_ok
