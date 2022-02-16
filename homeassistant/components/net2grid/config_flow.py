"""Config flow for Net2Grid integration."""
from __future__ import annotations

from typing import Any

from net2grid import Device, Net2Grid, Net2GridConnectionError
import voluptuous as vol

from homeassistant.components import zeroconf
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN


class Net2GridFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Net2Grid integration."""

    VERSION = 1
    discovered_host: str
    discovered_device: Device

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""

        errors = {}

        if user_input is not None:
            try:
                device = await self._async_get_device(user_input[CONF_HOST])
            except Net2GridConnectionError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(device.n2g_id)
                self._abort_if_unique_id_configured(
                    updates={CONF_HOST: user_input[CONF_HOST]}
                )
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_HOST: user_input[CONF_HOST],
                    },
                )
        else:
            user_input = {}

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
            errors=errors or {},
        )

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> FlowResult:
        """Handle zeroconf discovery."""
        self.discovered_host = discovery_info.host
        try:
            self.discovered_device = await self._async_get_device(discovery_info.host)
        except Net2GridConnectionError:
            return self.async_abort(reason="cannot_connect")

        await self.async_set_unique_id(self.discovered_device.n2g_id)
        self._abort_if_unique_id_configured(updates={CONF_HOST: discovery_info.host})

        self.context.update(
            {
                "title_placeholders": {
                    CONF_HOST: self.discovered_host,
                    "model": self.discovered_device.model,
                    CONF_NAME: self.discovered_device.manufacturer,
                },
            }
        )
        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by zeroconf."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data={
                    CONF_HOST: self.discovered_host,
                },
            )

        return self.async_show_form(
            step_id="zeroconf_confirm",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_NAME, default=self.hass.config.location_name
                    ): str,
                }
            ),
            description_placeholders={CONF_NAME: "Net2Grid"},
        )

    async def _async_get_device(self, host: str) -> Device:
        """Get device information from Net2Grid device."""
        session = async_get_clientsession(self.hass)
        net2grid = Net2Grid(host, session=session)
        return await net2grid.device()
