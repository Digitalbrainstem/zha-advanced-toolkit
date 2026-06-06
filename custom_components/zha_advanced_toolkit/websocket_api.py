"""Websocket API for ZHA Advanced Toolkit."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .models import (
    CommandEntityDescription,
    NumberEntityDescription,
    SelectEntityDescription,
    SwitchEntityDescription,
    ToolkitData,
)
from .zha import (
    async_read_cluster_attribute,
    async_write_cluster_attribute,
    resolve_zha_device,
)

_LOGGER = logging.getLogger(__name__)


TYPE_DEVICES = f"{DOMAIN}/devices"
TYPE_READ = f"{DOMAIN}/read"
TYPE_WRITE = f"{DOMAIN}/write"
TYPE_COMMAND = f"{DOMAIN}/command"
TYPE_RAW_CLUSTERS = f"{DOMAIN}/raw_clusters"
TYPE_RAW_READ = f"{DOMAIN}/raw_read"
TYPE_RAW_WRITE = f"{DOMAIN}/raw_write"


def _get_data(hass: HomeAssistant) -> ToolkitData:
    """Return the toolkit runtime data."""
    entries = hass.data.get(DOMAIN, {})
    if not entries:
        raise HomeAssistantError("ZHA Advanced Toolkit is not loaded")
    return next(iter(entries.values()))


def _find_device(data: ToolkitData, ieee: str):
    """Find a toolkit device by IEEE."""
    for device in data.devices:
        if device.ieee == ieee:
            return device
    raise HomeAssistantError(f"Unknown toolkit device {ieee}")


def _find_setting(device, key: str):
    """Find a setting by key."""
    for setting in device.settings:
        if setting.key == key:
            return setting
    raise HomeAssistantError(f"Unknown setting {key}")


def _find_command(device, key: str):
    """Find a command by key."""
    for command in device.commands:
        if command.key == key:
            return command
    raise HomeAssistantError(f"Unknown command {key}")


def _setting_payload(setting) -> dict[str, Any]:
    """Serialize a setting description for the panel."""
    payload: dict[str, Any] = {
        "key": setting.key,
        "name": setting.name,
        "category": setting.category,
        "cluster_id": setting.cluster_id,
        "attribute_id": setting.attribute_id,
        "attribute_name": setting.attribute_name,
        "enabled_by_default": setting.enabled_by_default,
    }
    if isinstance(setting, SelectEntityDescription):
        payload["type"] = "select"
        payload["options"] = [
            {"value": option.value, "label": option.label}
            for option in setting.options
        ]
        payload["custom_option"] = setting.custom_option
    elif isinstance(setting, SwitchEntityDescription):
        payload["type"] = "switch"
    elif isinstance(setting, NumberEntityDescription):
        payload["type"] = "number"
        payload["min"] = setting.native_min_value
        payload["max"] = setting.native_max_value
        payload["step"] = setting.native_step
        payload["unit"] = setting.native_unit_of_measurement
    else:
        payload["type"] = "unknown"
    return payload


def _command_payload(command: CommandEntityDescription) -> dict[str, Any]:
    """Serialize a command description for the panel."""
    return {
        "key": command.key,
        "name": command.name,
        "category": command.category,
        "cluster_id": command.cluster_id,
        "command_id": command.command_id,
        "params": command.params,
        "enabled_by_default": command.enabled_by_default,
    }


def _serialize_raw_clusters(live_device) -> list[dict[str, Any]]:
    """Serialize all exposed clusters and attributes from a live ZHA device."""
    result: list[dict[str, Any]] = []
    clusters_by_endpoint = live_device.async_get_clusters()
    for endpoint_id, clusters in clusters_by_endpoint.items():
        for cluster_type in ("in", "out"):
            for cluster_id, cluster in clusters.get(cluster_type, {}).items():
                attributes: list[dict[str, Any]] = []
                try:
                    cluster_attributes = live_device.async_get_cluster_attributes(
                        endpoint_id,
                        cluster_id,
                        cluster_type,
                    )
                except Exception as err:
                    _LOGGER.debug(
                        "Unable to list attributes for endpoint %s cluster 0x%04x: %s",
                        endpoint_id,
                        cluster_id,
                        err,
                    )
                    cluster_attributes = None
                if cluster_attributes:
                    attributes = [
                        {"id": attr_id, "name": getattr(attr, "name", str(attr_id))}
                        for attr_id, attr in cluster_attributes.items()
                    ]
                result.append(
                    {
                        "endpoint_id": endpoint_id,
                        "cluster_type": cluster_type,
                        "cluster_id": cluster_id,
                        "name": cluster.__class__.__name__,
                        "attributes": attributes,
                    }
                )
    return result


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): TYPE_DEVICES})
@websocket_api.async_response
async def websocket_devices(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return supported toolkit devices and profile metadata."""
    data = _get_data(hass)
    connection.send_result(
        msg["id"],
        [
            {
                "ieee": device.ieee,
                "name": device.name,
                "manufacturer": device.manufacturer,
                "model": device.model,
                "firmware": device.firmware,
                "profile": device.profile_name,
                "settings": [_setting_payload(setting) for setting in device.settings],
                "commands": [_command_payload(command) for command in device.commands],
            }
            for device in data.devices
        ],
    )


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): TYPE_READ,
        vol.Required("ieee"): str,
        vol.Required("key"): str,
    }
)
@websocket_api.async_response
async def websocket_read(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Read a toolkit setting."""
    data = _get_data(hass)
    device = _find_device(data, msg["ieee"])
    setting = _find_setting(device, msg["key"])
    value = await setting.async_read(hass, device.zha_device)
    connection.send_result(msg["id"], {"value": value})


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): TYPE_WRITE,
        vol.Required("ieee"): str,
        vol.Required("key"): str,
        vol.Required("value"): vol.Any(int, bool, str, float),
    }
)
@websocket_api.async_response
async def websocket_write(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Write a toolkit setting."""
    data = _get_data(hass)
    device = _find_device(data, msg["ieee"])
    setting = _find_setting(device, msg["key"])
    await setting.async_write(hass, device.zha_device, msg["value"])
    connection.send_result(msg["id"], {"value": msg["value"]})


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): TYPE_COMMAND,
        vol.Required("ieee"): str,
        vol.Required("key"): str,
    }
)
@websocket_api.async_response
async def websocket_command(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Issue a toolkit command."""
    data = _get_data(hass)
    device = _find_device(data, msg["ieee"])
    command = _find_command(device, msg["key"])
    await command.async_issue(hass, device.zha_device)
    connection.send_result(msg["id"], {"ok": True})


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): TYPE_RAW_CLUSTERS,
        vol.Required("ieee"): str,
    }
)
@websocket_api.async_response
async def websocket_raw_clusters(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return all exposed ZHA clusters and attributes for a toolkit device."""
    data = _get_data(hass)
    device = _find_device(data, msg["ieee"])
    live_device = resolve_zha_device(hass, device.zha_device)
    if live_device is None:
        raise HomeAssistantError("ZHA device is not ready")
    connection.send_result(msg["id"], _serialize_raw_clusters(live_device))


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): TYPE_RAW_READ,
        vol.Required("ieee"): str,
        vol.Required("endpoint_id"): int,
        vol.Required("cluster_id"): int,
        vol.Required("cluster_type"): str,
        vol.Required("attribute_id"): int,
        vol.Optional("manufacturer"): vol.Any(int, None),
    }
)
@websocket_api.async_response
async def websocket_raw_read(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Read any exposed cluster attribute."""
    data = _get_data(hass)
    device = _find_device(data, msg["ieee"])
    value = await async_read_cluster_attribute(
        hass,
        device.zha_device,
        msg["endpoint_id"],
        msg["cluster_id"],
        msg["attribute_id"],
        cluster_type=msg["cluster_type"],
        manufacturer=msg.get("manufacturer"),
    )
    connection.send_result(msg["id"], {"value": value})


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): TYPE_RAW_WRITE,
        vol.Required("ieee"): str,
        vol.Required("endpoint_id"): int,
        vol.Required("cluster_id"): int,
        vol.Required("cluster_type"): str,
        vol.Required("attribute_id"): int,
        vol.Required("value"): vol.Any(int, bool, str, float),
        vol.Optional("manufacturer"): vol.Any(int, None),
    }
)
@websocket_api.async_response
async def websocket_raw_write(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Write any exposed cluster attribute."""
    data = _get_data(hass)
    device = _find_device(data, msg["ieee"])
    await async_write_cluster_attribute(
        hass,
        device.zha_device,
        msg["endpoint_id"],
        msg["cluster_id"],
        msg["attribute_id"],
        msg["value"],
        cluster_type=msg["cluster_type"],
        manufacturer=msg.get("manufacturer"),
    )
    connection.send_result(msg["id"], {"value": msg["value"]})


def async_register_websocket_api(hass: HomeAssistant) -> None:
    """Register websocket commands."""
    websocket_api.async_register_command(hass, websocket_devices)
    websocket_api.async_register_command(hass, websocket_read)
    websocket_api.async_register_command(hass, websocket_write)
    websocket_api.async_register_command(hass, websocket_command)
    websocket_api.async_register_command(hass, websocket_raw_clusters)
    websocket_api.async_register_command(hass, websocket_raw_read)
    websocket_api.async_register_command(hass, websocket_raw_write)
