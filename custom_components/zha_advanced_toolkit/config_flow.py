"""Config flow for ZHA Advanced Toolkit."""

from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN


class ZHAAdvancedToolkitConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ZHA Advanced Toolkit."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Create the single toolkit config entry."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="ZHA Advanced Toolkit", data={})

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return the options flow."""
        return ZHAAdvancedToolkitOptionsFlow()


class ZHAAdvancedToolkitOptionsFlow(config_entries.OptionsFlow):
    """No-op options flow placeholder."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.OptionsFlowResult:
        """Show current options."""
        return self.async_create_entry(title="", data={})
