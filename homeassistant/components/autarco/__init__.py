"""The Autarco integration."""
from __future__ import annotations

from typing import NamedTuple

from autarco import Account, Autarco, Solar

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_PUBLIC_KEY, DOMAIN, LOGGER, SCAN_INTERVAL

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Autarco from a config entry."""

    coordinator = AutarcoDataUpdateCoordinator(hass)
    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:
        await coordinator.autarco.close()
        raise

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Autarco config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        del hass.data[DOMAIN][entry.entry_id]
    return unload_ok


class AutarcoData(NamedTuple):
    """Class for defining data in dict."""

    account: Account
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
        )
