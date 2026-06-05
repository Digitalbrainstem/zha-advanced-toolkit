"""Button entities for ZHA Advanced Toolkit."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .entity import ZHAAdvancedEntity
from .models import CommandEntityDescription, ToolkitData


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up button entities."""
    data: ToolkitData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        ZHAAdvancedButton(device, command)
        for device in data.devices
        for command in device.commands
    )


class ZHAAdvancedButton(ZHAAdvancedEntity, ButtonEntity):
    """A button that issues a predefined ZHA cluster command."""

    entity_description: CommandEntityDescription

    def __init__(self, toolkit_device, command: CommandEntityDescription) -> None:
        """Initialize the button."""
        super().__init__(toolkit_device, command)
        self.entity_description = command

    async def async_press(self) -> None:
        """Issue the configured Zigbee command."""
        await self.entity_description.async_issue(self.hass, self.toolkit_device.zha_device)
