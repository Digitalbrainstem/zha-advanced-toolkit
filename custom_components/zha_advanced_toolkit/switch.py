"""Switch entities for ZHA Advanced Toolkit."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .entity import ZHAAdvancedEntity
from .models import SwitchEntityDescription, ToolkitData


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up switch entities."""
    data: ToolkitData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        ZHAAdvancedSwitch(device, setting)
        for device in data.devices
        for setting in device.settings
        if isinstance(setting, SwitchEntityDescription)
    )


class ZHAAdvancedSwitch(ZHAAdvancedEntity, SwitchEntity):
    """A switch backed by a ZHA cluster attribute."""

    entity_description: SwitchEntityDescription
    _attr_should_poll = False

    def __init__(self, toolkit_device, description: SwitchEntityDescription) -> None:
        """Initialize the switch."""
        super().__init__(toolkit_device, description)
        self.entity_description = description
        self._attr_is_on: bool | None = None
        self._raw_value = None

    async def async_added_to_hass(self) -> None:
        """Read the current value when added."""
        await self.async_update()

    async def async_update(self) -> None:
        """Refresh the current value."""
        try:
            self._raw_value = await self.entity_description.async_read(
                self.hass, self.toolkit_device.zha_device
            )
        except HomeAssistantError:
            self._attr_zigbee_available = False
            return
        self._attr_zigbee_available = True
        self._attr_is_on = self.entity_description.value_to_bool(self._raw_value)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the setting on."""
        await self._async_set_value(True)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the setting off."""
        await self._async_set_value(False)

    async def _async_set_value(self, value: bool) -> None:
        """Set the Zigbee attribute value."""
        raw_value = self.entity_description.bool_to_value(value)
        await self.entity_description.async_write(
            self.hass, self.toolkit_device.zha_device, raw_value
        )
        self._raw_value = raw_value
        self._attr_is_on = value
        self.async_write_ha_state()
