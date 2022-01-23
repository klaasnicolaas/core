"""Tests for the Net2Grid integration."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from net2grid import Net2GridConnectionError
import pytest

from homeassistant.components.net2grid.const import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry


@pytest.mark.parametrize("mock_net2grid", ["net2grid/device.json"], indirect=True)
async def test_load_unload_config_entry(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_net2grid: AsyncMock,
) -> None:
    """Test the Net2Grid configuration entry unloading."""
    connection_connected = asyncio.Future()
    connection_finished = asyncio.Future()

    async def connect(callback: Callable):
        connection_connected.set_result(None)
        await connection_finished

    # Mock out net2grid.listen with a Future
    mock_net2grid.listen.side_effect = connect

    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    await connection_connected

    # Ensure config entry is loaded and are connected
    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert mock_net2grid.connect.call_count == 1
    assert mock_net2grid.disconnect.call_count == 0

    await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Ensure everything is cleaned up nicely and are disconnected
    assert mock_net2grid.disconnect.call_count == 1
    assert not hass.data.get(DOMAIN)


@patch(
    "homeassistant.components.net2grid.Net2Grid.request",
    side_effect=Net2GridConnectionError,
)
async def test_config_entry_not_ready(
    mock_request: MagicMock,
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test the Net2Grid configuration entry not ready."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_request.call_count == 1
    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_setting_unique_id(
    hass: HomeAssistant, init_integration: MockConfigEntry
) -> None:
    """Test we set unique ID if not set yet."""
    assert hass.data[DOMAIN]
    assert init_integration.unique_id == "unique_thingy"
