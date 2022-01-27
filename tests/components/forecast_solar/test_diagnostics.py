"""Tests for the diagnostics data provided by the Forecast.Solar integration."""
from aiohttp import ClientSession

from homeassistant.components.diagnostics import REDACTED
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry
from tests.components.diagnostics import get_diagnostics_for_config_entry


async def test_diagnostics(
    hass: HomeAssistant,
    hass_client: ClientSession,
    init_integration: MockConfigEntry,
):
    """Test diagnostics."""
    assert await get_diagnostics_for_config_entry(
        hass, hass_client, init_integration
    ) == {
        "entry": {
            "title": "Green House",
            "data": {
                "latitude": REDACTED,
                "longitude": REDACTED,
            },
            "options": {
                "api_key": REDACTED,
                "azimuth": 190,
                "damping": 0.5,
                "declination": 30,
                "modules power": 5100,
            },
        }
    }
