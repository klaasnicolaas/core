"""Coordinator for the PowerFox integration."""
from __future__ import annotations

from powerfox import Powerfox

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER, SCAN_INTERVAL


class PowerfoxDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Powerfox data."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the data update coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

        self.powerfox = Powerfox(
            username=self.config_entry.data[CONF_USERNAME],
            password=self.config_entry.data[CONF_PASSWORD],
            session=async_get_clientsession(hass),
        )
