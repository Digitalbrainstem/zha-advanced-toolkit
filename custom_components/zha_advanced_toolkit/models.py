"""Data models for ZHA Advanced Toolkit profiles and entities."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
import re
from typing import Any

from homeassistant.components.number import NumberMode
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import CLUSTER_TYPE_IN, COMMAND_TYPE_SERVER
from .zha import (
    async_issue_cluster_command,
    async_read_cluster_attribute,
    async_write_cluster_attribute,
    cluster_attribute_supported,
    cluster_supported,
    get_device_firmware,
    get_device_ieee,
    get_device_manufacturer,
    get_device_model,
    get_device_name,
)

def _parse_version(value: str | None) -> tuple[int, ...] | None:
    """Parse a firmware-ish version string into comparable integer parts."""
    if not value:
        return None
    parts = [int(part) for part in re.findall(r"\d+", value)]
    return tuple(parts) if parts else None


def _version_supported(
    firmware: str | None,
    min_firmware: str | None,
    max_firmware: str | None,
) -> bool:
    """Return whether a setting supports a firmware version."""
    parsed = _parse_version(firmware)
    if parsed is None:
        return True
    minimum = _parse_version(min_firmware)
    maximum = _parse_version(max_firmware)
    if minimum is not None and parsed < minimum:
        return False
    if maximum is not None and parsed > maximum:
        return False
    return True


@dataclass(frozen=True, kw_only=True)
class Option:
    """A select option."""

    value: int
    label: str


@dataclass(frozen=True, kw_only=True)
class EntityDescriptionBase:
    """Common metadata for generated toolkit entities."""

    key: str
    name: str
    category: str
    endpoint_id: int
    cluster_id: int
    cluster_type: str = CLUSTER_TYPE_IN
    manufacturer: int | None = None
    min_firmware: str | None = None
    max_firmware: str | None = None

    @property
    def unique_suffix(self) -> str:
        """Return stable unique suffix."""
        return f"{self.endpoint_id}-{self.cluster_id:04x}-{self.key}"

    def supports_firmware(self, firmware: str | None) -> bool:
        """Return whether the firmware supports this entity."""
        return _version_supported(firmware, self.min_firmware, self.max_firmware)

    def is_supported_by_device(self, zha_device: Any) -> bool:
        """Return whether the device exposes the target cluster."""
        return cluster_supported(
            zha_device,
            self.endpoint_id,
            self.cluster_id,
            self.cluster_type,
        )


@dataclass(frozen=True, kw_only=True)
class AttributeEntityDescription(EntityDescriptionBase):
    """Metadata for an attribute-backed entity."""

    attribute_id: int
    attribute_name: str | None = None
    read_only: bool = False

    @property
    def unique_suffix(self) -> str:
        """Return stable unique suffix."""
        return f"{self.endpoint_id}-{self.cluster_id:04x}-{self.attribute_id:04x}"

    def is_supported_by_device(self, zha_device: Any) -> bool:
        """Return whether the device exposes the target attribute."""
        return cluster_attribute_supported(
            zha_device,
            self.endpoint_id,
            self.cluster_id,
            self.cluster_type,
            self.attribute_id,
            self.attribute_name,
        )

    async def async_read(self, zha_device: Any) -> Any:
        """Read the current Zigbee attribute value."""
        return await async_read_cluster_attribute(
            zha_device,
            self.endpoint_id,
            self.cluster_id,
            self.attribute_id,
            cluster_type=self.cluster_type,
            manufacturer=self.manufacturer,
        )

    async def async_write(self, hass: HomeAssistant, zha_device: Any, value: Any) -> None:
        """Write a Zigbee attribute value."""
        if self.read_only:
            raise HomeAssistantError(f"{self.name} is read-only")

        await async_write_cluster_attribute(
            hass,
            zha_device,
            self.endpoint_id,
            self.cluster_id,
            self.attribute_id,
            value,
            cluster_type=self.cluster_type,
            manufacturer=self.manufacturer,
        )


@dataclass(frozen=True, kw_only=True)
class SelectEntityDescription(AttributeEntityDescription):
    """Metadata for a select entity."""

    options: tuple[Option, ...]
    custom_option: bool = True

    @property
    def option_labels(self) -> list[str]:
        """Return HA select labels."""
        labels = [option.label for option in self.options]
        if self.custom_option:
            labels.append("Custom / Unknown")
        return labels

    def value_to_label(self, value: Any) -> str | None:
        """Convert a raw Zigbee value to a select label."""
        for option in self.options:
            if option.value == value:
                return option.label
        if self.custom_option:
            return "Custom / Unknown"
        return None

    def label_to_value(self, label: str) -> int:
        """Convert a select label to a raw Zigbee value."""
        for option in self.options:
            if option.label == label:
                return option.value
        raise HomeAssistantError(
            f"{self.name} value {label!r} is not a predefined option"
        )


@dataclass(frozen=True, kw_only=True)
class SwitchEntityDescription(AttributeEntityDescription):
    """Metadata for a switch entity."""

    on_value: int | bool = 1
    off_value: int | bool = 0

    def value_to_bool(self, value: Any) -> bool | None:
        """Convert a raw Zigbee value to a boolean."""
        if value == self.on_value:
            return True
        if value == self.off_value:
            return False
        return None

    def bool_to_value(self, value: bool) -> int | bool:
        """Convert a boolean to a raw Zigbee value."""
        return self.on_value if value else self.off_value


@dataclass(frozen=True, kw_only=True)
class NumberEntityDescription(AttributeEntityDescription):
    """Metadata for a number entity."""

    native_min_value: float
    native_max_value: float
    native_step: float = 1
    native_unit_of_measurement: str | None = None
    mode: NumberMode = NumberMode.BOX


@dataclass(frozen=True, kw_only=True)
class CommandEntityDescription(EntityDescriptionBase):
    """Metadata for a command button."""

    command_id: int
    command_type: str = COMMAND_TYPE_SERVER
    params: Mapping[str, Any] | None = None
    args: Sequence[Any] | None = None

    @property
    def unique_suffix(self) -> str:
        """Return stable unique suffix."""
        param_suffix = ""
        if self.params:
            param_suffix = "-" + "-".join(f"{key}-{value}" for key, value in self.params.items())
        return f"{self.endpoint_id}-{self.cluster_id:04x}-cmd-{self.command_id:02x}{param_suffix}"

    async def async_issue(self, hass: HomeAssistant, zha_device: Any) -> None:
        """Issue the configured Zigbee command."""
        await async_issue_cluster_command(
            hass,
            zha_device,
            self.endpoint_id,
            self.cluster_id,
            self.command_id,
            self.command_type,
            args=list(self.args) if self.args is not None else None,
            params=dict(self.params) if self.params is not None else None,
            cluster_type=self.cluster_type,
            manufacturer=self.manufacturer,
        )


@dataclass(frozen=True, kw_only=True)
class Profile:
    """Device profile containing friendly settings."""

    name: str
    manufacturer: str
    model: str
    settings: tuple[AttributeEntityDescription, ...] = field(default_factory=tuple)
    commands: tuple[CommandEntityDescription, ...] = field(default_factory=tuple)

    def matches(self, manufacturer: str | None, model: str | None) -> bool:
        """Return whether this profile matches a ZHA device."""
        return (
            (manufacturer or "").casefold() == self.manufacturer.casefold()
            and (model or "").casefold() == self.model.casefold()
        )

    def create_device(
        self,
        zha_device: Any,
        settings: Sequence[AttributeEntityDescription],
        commands: Sequence[CommandEntityDescription],
    ) -> "ToolkitDevice":
        """Create a runtime device wrapper."""
        return ToolkitDevice(
            zha_device=zha_device,
            profile_name=self.name,
            settings=tuple(settings),
            commands=tuple(commands),
        )


@dataclass(frozen=True)
class ToolkitDevice:
    """Runtime toolkit device wrapper."""

    zha_device: Any
    profile_name: str
    settings: tuple[AttributeEntityDescription, ...]
    commands: tuple[CommandEntityDescription, ...]

    @property
    def ieee(self) -> str:
        """Return the device IEEE address."""
        return get_device_ieee(self.zha_device)

    @property
    def manufacturer(self) -> str | None:
        """Return manufacturer."""
        return get_device_manufacturer(self.zha_device)

    @property
    def model(self) -> str | None:
        """Return model."""
        return get_device_model(self.zha_device)

    @property
    def name(self) -> str:
        """Return display name."""
        return get_device_name(self.zha_device) or f"{self.manufacturer or 'Zigbee'} {self.model or 'device'}"

    @property
    def firmware(self) -> str | None:
        """Return firmware version."""
        return get_device_firmware(self.zha_device)


@dataclass
class ToolkitData:
    """Integration runtime data."""

    devices: list[ToolkitDevice]


def option(value: int, label: str) -> Option:
    """Create a select option."""
    return Option(value=value, label=label)
