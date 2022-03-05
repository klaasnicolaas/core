"""DataUpdateCoordinator for the Autarco integration."""
from __future__ import annotations

from typing import NamedTuple

from autarco import Account, Autarco, Inverter, Solar

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_PUBLIC_KEY, DOMAIN, LOGGER, SCAN_INTERVAL


class AutarcoData(NamedTuple):
    """Class for defining data in dict."""

    account: Account
    inverters: dict[str, Inverter]
    solar: Solar


class AutarcoDataUpdateCoordinator(DataUpdateCoordinator[AutarcoData]):
    """Class to manage fetching Autarco data from single eindpoint."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the data update coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

        self.autarco = Autarco(
            email=self.config_entry.data[CONF_EMAIL],
            password=self.config_entry.data[CONF_PASSWORD],
            session=async_get_clientsession(hass),
        )

    async def _async_update_data(self) -> AutarcoData:
        """Update data from Autarco."""
        return AutarcoData(
            account=await self.autarco.account(self.config_entry.data[CONF_PUBLIC_KEY]),
            solar=await self.autarco.solar(self.config_entry.data[CONF_PUBLIC_KEY]),
            inverters=await self.autarco.all_inverters(
                self.config_entry.data[CONF_PUBLIC_KEY]
            ),
        )
