"""Select entities for ZHA Advanced Toolkit."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .entity import ZHAAdvancedEntity
from .models import SelectEntityDescription, ToolkitData


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up select entities."""
    data: ToolkitData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        ZHAAdvancedSelect(device, setting)
        for device in data.devices
        for setting in device.settings
        if isinstance(setting, SelectEntityDescription)
    )


class ZHAAdvancedSelect(ZHAAdvancedEntity, SelectEntity):
    """A select backed by a ZHA cluster attribute."""

    entity_description: SelectEntityDescription
    _attr_should_poll = False

    def __init__(self, toolkit_device, description: SelectEntityDescription) -> None:
        """Initialize the select."""
        super().__init__(toolkit_device, description)
        self.entity_description = description
        self._attr_options = description.option_labels
        self._attr_current_option: str | None = None
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
        self._attr_current_option = self.entity_description.value_to_label(
            self._raw_value
        )

    async def async_select_option(self, option: str) -> None:
        """Set the Zigbee attribute value."""
        value = self.entity_description.label_to_value(option)
        await self.entity_description.async_write(
            self.hass, self.toolkit_device.zha_device, value
        )
        self._raw_value = value
        self._attr_current_option = option
        self.async_write_ha_state()
