"""Small compatibility layer around ZHA internals and services."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr

from .const import CLUSTER_TYPE_IN


class ZHAAccessError(HomeAssistantError):
    """Raised when ZHA is unavailable or incompatible."""


@dataclass(frozen=True, kw_only=True)
class ZHADeviceRef:
    """Stable reference to a ZHA device from Home Assistant's device registry."""

    ieee: str
    manufacturer: str | None
    model: str | None
    name: str | None
    firmware: str | None


def _get_zha_gateway(hass: HomeAssistant) -> Any:
    """Return the active ZHA gateway."""
    try:
        from homeassistant.components.zha.helpers import get_zha_gateway
    except ImportError as err:
        raise ZHAAccessError("ZHA integration helpers are unavailable") from err

    try:
        return get_zha_gateway(hass)
    except Exception as err:
        raise ZHAAccessError("ZHA is not ready") from err


def _get_zha_gateway_proxy(hass: HomeAssistant) -> Any | None:
    """Return the active ZHA gateway proxy if available."""
    try:
        from homeassistant.components.zha.helpers import get_zha_gateway_proxy
    except ImportError:
        return None

    try:
        return get_zha_gateway_proxy(hass)
    except Exception:
        return None


def get_zha_devices(hass: HomeAssistant) -> list[Any]:
    """Return ZHA devices from the device registry, with live ZHA fallback.

    The device registry is restored before ZHA finishes gateway initialization, so it
    is the reliable source for creating entities during Home Assistant startup.
    """
    registry = dr.async_get(hass)
    devices = _get_registry_zha_devices(registry)
    if devices:
        return devices

    return _get_live_zha_devices(hass)


def _get_registry_zha_devices(registry: dr.DeviceRegistry) -> list[ZHADeviceRef]:
    """Return ZHA device references from the Home Assistant device registry."""
    registry_devices = getattr(registry, "devices", {})
    entries = (
        registry_devices.values()
        if hasattr(registry_devices, "values")
        else registry_devices
    )

    devices: list[ZHADeviceRef] = []
    seen: set[str] = set()
    for entry in entries:
        ieee = _entry_zha_ieee(entry)
        if not ieee or ieee in seen:
            continue
        seen.add(ieee)
        devices.append(
            ZHADeviceRef(
                ieee=ieee,
                manufacturer=getattr(entry, "manufacturer", None),
                model=getattr(entry, "model", None),
                name=(
                    getattr(entry, "name_by_user", None)
                    or getattr(entry, "name", None)
                    or getattr(entry, "original_name", None)
                ),
                firmware=getattr(entry, "sw_version", None),
            )
        )
    return devices


def _entry_zha_ieee(entry: Any) -> str | None:
    """Extract a ZHA IEEE string from a device registry entry."""
    for identifier_tuple in getattr(entry, "identifiers", set()):
        if len(identifier_tuple) < 2:
            continue
        domain, identifier = identifier_tuple[:2]
        if domain == "zha":
            return str(identifier)

    for connection_tuple in getattr(entry, "connections", set()):
        if len(connection_tuple) < 2:
            continue
        connection_type, identifier = connection_tuple[:2]
        if connection_type == dr.CONNECTION_ZIGBEE:
            return str(identifier)
    return None


def _get_live_zha_devices(hass: HomeAssistant) -> list[Any]:
    """Return live ZHA gateway devices if the gateway is ready."""
    devices: list[Any] = []
    gateway_proxy = _get_zha_gateway_proxy(hass)
    if gateway_proxy is not None:
        for device_proxy in getattr(gateway_proxy, "device_proxies", {}).values():
            device = getattr(device_proxy, "device", None)
            if device is not None:
                devices.append(device)

    try:
        gateway = _get_zha_gateway(hass)
    except ZHAAccessError:
        return devices

    for device in getattr(gateway, "devices", {}).values():
        if all(get_device_ieee(device) != get_device_ieee(existing) for existing in devices):
            devices.append(device)
    return devices


def _nested_device(zha_device: Any) -> Any:
    """Return the nested zigpy device if present."""
    if isinstance(zha_device, ZHADeviceRef):
        return zha_device
    return getattr(zha_device, "device", None) or zha_device


def _first_attr(zha_device: Any, names: tuple[str, ...]) -> Any:
    """Return the first present attribute from the ZHA wrapper or nested device."""
    nested = _nested_device(zha_device)
    for source in (zha_device, nested):
        for name in names:
            value = getattr(source, name, None)
            if value not in (None, ""):
                return value
    return None


def get_device_ieee(zha_device: Any) -> str:
    """Return a device IEEE string."""
    if isinstance(zha_device, ZHADeviceRef):
        return zha_device.ieee
    return str(_first_attr(zha_device, ("ieee",)) or "")


def get_device_manufacturer(zha_device: Any) -> str | None:
    """Return a device manufacturer."""
    if isinstance(zha_device, ZHADeviceRef):
        return zha_device.manufacturer
    value = _first_attr(zha_device, ("manufacturer",))
    return str(value) if value is not None else None


def get_device_model(zha_device: Any) -> str | None:
    """Return a device model."""
    if isinstance(zha_device, ZHADeviceRef):
        return zha_device.model
    value = _first_attr(zha_device, ("model",))
    return str(value) if value is not None else None


def get_device_name(zha_device: Any) -> str | None:
    """Return a device name."""
    if isinstance(zha_device, ZHADeviceRef):
        return zha_device.name
    value = _first_attr(zha_device, ("name",))
    return str(value) if value is not None else None


def get_device_firmware(zha_device: Any) -> str | None:
    """Return a device firmware version."""
    if isinstance(zha_device, ZHADeviceRef):
        return zha_device.firmware
    value = _first_attr(
        zha_device,
        ("firmware_version", "sw_version", "software_build_id"),
    )
    return str(value) if value is not None else None


def resolve_zha_device(hass: HomeAssistant, zha_device: Any) -> Any | None:
    """Resolve a registry device reference to a live ZHA device."""
    if not isinstance(zha_device, ZHADeviceRef):
        return zha_device

    target_ieee = zha_device.ieee
    for live_device in _get_live_zha_devices(hass):
        if get_device_ieee(live_device) == target_ieee:
            return live_device
    return None


def _get_cluster(
    zha_device: Any,
    endpoint_id: int,
    cluster_id: int,
    cluster_type: str = CLUSTER_TYPE_IN,
) -> Any | None:
    """Return a cluster if available."""
    try:
        return zha_device.async_get_cluster(
            endpoint_id,
            cluster_id,
            cluster_type=cluster_type,
        )
    except Exception:
        return None


def cluster_supported(
    zha_device: Any,
    endpoint_id: int,
    cluster_id: int,
    cluster_type: str = CLUSTER_TYPE_IN,
) -> bool:
    """Return whether a device exposes a cluster."""
    return _get_cluster(zha_device, endpoint_id, cluster_id, cluster_type) is not None


def cluster_attribute_supported(
    zha_device: Any,
    endpoint_id: int,
    cluster_id: int,
    cluster_type: str,
    attribute_id: int,
    attribute_name: str | None,
) -> bool:
    """Return whether a device exposes an attribute definition."""
    try:
        attributes = zha_device.async_get_cluster_attributes(
            endpoint_id,
            cluster_id,
            cluster_type,
        )
    except Exception:
        attributes = None

    if not attributes:
        return cluster_supported(zha_device, endpoint_id, cluster_id, cluster_type)

    if attribute_id in attributes:
        return True

    return any(
        getattr(attribute, "name", None) == attribute_name
        for attribute in attributes.values()
    )


async def async_read_cluster_attribute(
    hass: HomeAssistant,
    zha_device: Any,
    endpoint_id: int,
    cluster_id: int,
    attribute_id: int,
    *,
    cluster_type: str = CLUSTER_TYPE_IN,
    manufacturer: int | None = None,
) -> Any:
    """Read a cluster attribute from a ZHA device."""
    live_device = resolve_zha_device(hass, zha_device)
    if live_device is None:
        raise HomeAssistantError("ZHA device is not ready")

    cluster = _get_cluster(live_device, endpoint_id, cluster_id, cluster_type)
    if cluster is None:
        raise HomeAssistantError(
            f"Cluster 0x{cluster_id:04x} endpoint {endpoint_id} is unavailable"
        )

    kwargs: dict[str, Any] = {
        "allow_cache": False,
        "only_cache": False,
    }
    if manufacturer is not None:
        kwargs["manufacturer"] = manufacturer

    success, failure = await cluster.read_attributes([attribute_id], **kwargs)
    if failure:
        raise HomeAssistantError(
            f"Failed to read attribute 0x{attribute_id:04x}: {failure}"
        )
    return success.get(attribute_id)


async def async_write_cluster_attribute(
    hass: HomeAssistant,
    zha_device: Any,
    endpoint_id: int,
    cluster_id: int,
    attribute_id: int,
    value: Any,
    *,
    cluster_type: str = CLUSTER_TYPE_IN,
    manufacturer: int | None = None,
) -> None:
    """Write a cluster attribute using ZHA's registered service."""
    data: dict[str, Any] = {
        "ieee": get_device_ieee(zha_device),
        "endpoint_id": endpoint_id,
        "cluster_id": cluster_id,
        "cluster_type": cluster_type,
        "attribute": attribute_id,
        "value": value,
    }
    if manufacturer is not None:
        data["manufacturer"] = manufacturer

    await hass.services.async_call(
        "zha",
        "set_zigbee_cluster_attribute",
        data,
        blocking=True,
    )


async def async_issue_cluster_command(
    hass: HomeAssistant,
    zha_device: Any,
    endpoint_id: int,
    cluster_id: int,
    command_id: int,
    command_type: str,
    *,
    args: list[Any] | None,
    params: dict[str, Any] | None,
    cluster_type: str = CLUSTER_TYPE_IN,
    manufacturer: int | None = None,
) -> None:
    """Issue a cluster command using ZHA's registered service."""
    data: dict[str, Any] = {
        "ieee": get_device_ieee(zha_device),
        "endpoint_id": endpoint_id,
        "cluster_id": cluster_id,
        "cluster_type": cluster_type,
        "command": command_id,
        "command_type": command_type,
    }
    if args is not None:
        data["args"] = args
    if params is not None:
        data["params"] = params
    if manufacturer is not None:
        data["manufacturer"] = manufacturer

    await hass.services.async_call(
        "zha",
        "issue_zigbee_cluster_command",
        data,
        blocking=True,
    )
