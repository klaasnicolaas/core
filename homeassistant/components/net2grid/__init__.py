"""The Net2Grid integration."""
from __future__ import annotations

from typing import TypedDict

from net2grid import Device, Net2Grid, SmartBridge

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER, SCAN_INTERVAL, SERVICE_DEVICE, SERVICE_SMARTBRIDGE

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Net2Grid from a config entry."""

    coordinator = Net2GridDataUpdateCoordinator(hass)
    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:
        await coordinator.net2grid.close()
        raise

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Net2Grid config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        del hass.data[DOMAIN][entry.entry_id]
    return unload_ok


class Net2GridData(TypedDict):
    """Class for defining data in dict."""

    device: Device
    smartbridge: SmartBridge


class Net2GridDataUpdateCoordinator(DataUpdateCoordinator[Net2GridData]):
    """Class to manage fetching Net2Grid data from single eindpoint."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Initialize global Net2Grid data updater."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

        self.net2grid = Net2Grid(
            self.config_entry.data[CONF_HOST], session=async_get_clientsession(hass)
        )

    async def _async_update_data(self) -> Net2GridData:
        """Fetch data from SmartBridge."""
        data: Net2GridData = {
            SERVICE_DEVICE: await self.net2grid.device(),
            SERVICE_SMARTBRIDGE: await self.net2grid.smartbridge(),
        }
        return data
