"""Number entities for ZHA Advanced Toolkit."""

from __future__ import annotations

from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .entity import ZHAAdvancedEntity
from .models import NumberEntityDescription, ToolkitData


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up number entities."""
    data: ToolkitData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        ZHAAdvancedNumber(device, setting)
        for device in data.devices
        for setting in device.settings
        if isinstance(setting, NumberEntityDescription)
    )


class ZHAAdvancedNumber(ZHAAdvancedEntity, NumberEntity):
    """A number backed by a ZHA cluster attribute."""

    entity_description: NumberEntityDescription
    _attr_should_poll = False

    def __init__(self, toolkit_device, description: NumberEntityDescription) -> None:
        """Initialize the number."""
        super().__init__(toolkit_device, description)
        self.entity_description = description
        self._attr_native_value: float | None = None
        self._attr_native_min_value = description.native_min_value
        self._attr_native_max_value = description.native_max_value
        self._attr_native_step = description.native_step
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_mode = description.mode

    async def async_added_to_hass(self) -> None:
        """Read the current value when added."""
        await self.async_update()

    async def async_update(self) -> None:
        """Refresh the current value."""
        try:
            value = await self.entity_description.async_read(
                self.hass, self.toolkit_device.zha_device
            )
        except HomeAssistantError:
            self._attr_zigbee_available = False
            return
        self._attr_zigbee_available = True
        self._attr_native_value = None if value is None else float(value)

    async def async_set_native_value(self, value: float) -> None:
        """Set the Zigbee attribute value."""
        raw_value: Any
        if float(value).is_integer():
            raw_value = int(value)
        else:
            raw_value = value
        await self.entity_description.async_write(
            self.hass, self.toolkit_device.zha_device, raw_value
        )
        self._attr_native_value = value
        self.async_write_ha_state()
