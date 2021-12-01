"""The CEMM integration."""
from __future__ import annotations

from typing import TypedDict

from cemm import CEMM, Device, SmartMeter

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER, SCAN_INTERVAL, SERVICE_DEVICE, SERVICE_SMARTMETER

PLATFORMS = (SENSOR_DOMAIN,)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up CEMM from a config entry."""

    coordinator = CEMMDataUpdateCoordinator(hass)
    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:
        await coordinator.cemm.close()
        raise

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload CEMM config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.cemm.close()
    return unload_ok


class CEMMData(TypedDict):
    """Class for defining data in dict."""

    device: Device
    smartmeter: SmartMeter


class CEMMDataUpdateCoordinator(DataUpdateCoordinator[CEMMData]):
    """Class to manage fetching CEMM data from single endpoint."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Initialize global CEMM data updater."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

        self.cemm = CEMM(
            self.config_entry.data[CONF_HOST], session=async_get_clientsession(hass)
        )

    async def _async_update_data(self) -> CEMMData:
        """Fetch data from CEMM."""
        data: CEMMData = {
            SERVICE_DEVICE: await self.cemm.device(),
            SERVICE_SMARTMETER: await self.cemm.smartmeter(),
        }

        return data
