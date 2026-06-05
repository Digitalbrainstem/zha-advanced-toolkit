"""Base entities for ZHA Advanced Toolkit."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import ZHA_DOMAIN


class ZHAAdvancedEntity(Entity):
    """Base class for toolkit entities."""

    _attr_has_entity_name = True

    def __init__(self, toolkit_device, description) -> None:
        """Initialize the entity."""
        self.toolkit_device = toolkit_device
        self.entity_description = description
        self._attr_zigbee_available = True
        self._attr_unique_id = (
            f"{toolkit_device.ieee}-zat-{description.unique_suffix}"
        )
        self._attr_name = description.name
        self._attr_extra_state_attributes = {
            "category": description.category,
            "zha_cluster_id": f"0x{description.cluster_id:04x}",
            "zha_endpoint_id": description.endpoint_id,
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info and attach entities to the existing ZHA device."""
        return DeviceInfo(
            identifiers={(ZHA_DOMAIN, self.toolkit_device.ieee)},
            connections={(dr.CONNECTION_ZIGBEE, self.toolkit_device.ieee)},
            name=self.toolkit_device.name,
            manufacturer=self.toolkit_device.manufacturer,
            model=self.toolkit_device.model,
            sw_version=self.toolkit_device.firmware,
            configuration_url="homeassistant://config/devices/device",
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._attr_zigbee_available and bool(
            getattr(self.toolkit_device.zha_device, "available", True)
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return diagnostic attributes."""
        attributes = dict(self._attr_extra_state_attributes or {})
        if self.toolkit_device.profile_name:
            attributes["profile"] = self.toolkit_device.profile_name
        if self.toolkit_device.firmware:
            attributes["firmware"] = self.toolkit_device.firmware
        return attributes
