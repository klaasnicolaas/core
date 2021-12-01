"""Config flow for CEMM integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from core.homeassistant.config_entries import ConfigFlow
from core.homeassistant.const import CONF_HOST, CONF_NAME
from core.homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN


class CEMMFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for CEMM."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""

        errors = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_NAME, default=self.hass.config.location_name
                    ): str,
                    vol.Required(CONF_HOST): str,
                }
            ),
            errors=errors,
        )
