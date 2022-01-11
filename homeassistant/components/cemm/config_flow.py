"""Config flow for CEMM integration."""
from __future__ import annotations

from typing import Any

from cemm import CEMM, CEMMConnectionError
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_CONNECTIONS, DOMAIN


class CEMMFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for CEMM."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize with empty variables."""
        self.connections: list[dict[str, int | str]] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""

        errors = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            try:
                async with CEMM(host=user_input[CONF_HOST], session=session) as client:
                    await client.all_connections()
                    # for item in connections:
                    #     self.connections.append(item)
            except CEMMConnectionError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_CONNECTIONS: self.connections,
                    },
                )

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
