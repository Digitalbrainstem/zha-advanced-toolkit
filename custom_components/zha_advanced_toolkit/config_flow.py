"""Config flow for ZHA Advanced Toolkit."""

from __future__ import annotations

from typing import Any

from homeassistant import config_entries

from .const import DOMAIN


class ZHAAdvancedToolkitConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ZHA Advanced Toolkit."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ):
        """Create the single toolkit config entry."""
        await self.async_set_unique_id("zha_advanced_toolkit")
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="ZHA Advanced Toolkit", data={})
