"""Coordinator for the PowerFox integration."""
from __future__ import annotations

from powerfox import Powerfox, Poweropti

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER, SCAN_INTERVAL


class PowerfoxDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Powerfox data."""

    config_entry: ConfigEntry
    device_id: str
    powerfox: Powerfox

    def __init__(self, hass: HomeAssistant, device: Poweropti, client: Powerfox) -> None:
        """Initialize the data update coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

        self.device_id = device.device_id
        self.powerfox = client

    async def _async_update_data(self) -> Poweropti:
        """Fetch data from Powerfox."""
        return await self.powerfox.device(device_id=self.device_id)
