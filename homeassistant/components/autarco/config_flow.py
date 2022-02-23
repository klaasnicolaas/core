"""Config flow for Autarco integration."""
from __future__ import annotations

from typing import Any

from autarco import Autarco, AutarcoConnectionError
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_PUBLIC_KEY, DOMAIN


class AutarcoFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Autarco integration."""

    VERSION = 1
    public_key: str

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""

        errors = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            try:
                client = Autarco(
                    email=user_input[CONF_EMAIL],
                    password=user_input[CONF_PASSWORD],
                    session=session,
                )
                self.public_key = await client.get_public_key()
            except AutarcoConnectionError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title="Autarco",
                    data={
                        CONF_EMAIL: user_input[CONF_EMAIL],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        CONF_PUBLIC_KEY: self.public_key,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )
