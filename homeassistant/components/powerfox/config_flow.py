"""Config flow for Powerfox integration."""
from __future__ import annotations

from typing import Any

from powerfox import Powerfox, PowerfoxAuthenticationError, PowerfoxConnectionError
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN


class PowerfoxFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Powerfox integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""

        errors = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            try:
                async with Powerfox(
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                    session=session,
                ) as client:
                    await client.all_devices()
            except PowerfoxConnectionError:
                errors["base"] = "cannot_connect"
            except PowerfoxAuthenticationError:
                errors["base"] = "invalid_auth"
            else:
                return self.async_create_entry(
                    title="Powerfox",
                    data={
                        CONF_USERNAME: user_input[CONF_USERNAME],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
        )
