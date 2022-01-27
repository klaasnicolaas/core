"""Fixtures for Net2Grid integration tests."""
from collections.abc import Generator
import json
from unittest.mock import AsyncMock, MagicMock, patch

from net2grid import Device as Net2GridDevice, SmartBridge
import pytest

from homeassistant.components.net2grid.const import DOMAIN
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry, load_fixture


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return the default mocked config entry."""
    return MockConfigEntry(
        title="home",
        domain=DOMAIN,
        data={CONF_HOST: "192.168.1.123"},
        unique_id="unique_thingy",
    )


@pytest.fixture
def mock_setup_entry() -> Generator[None, None, None]:
    """Mock setting up a config entry."""
    with patch(
        "homeassistant.components.net2grid.async_setup_entry", return_value=True
    ):
        yield


@pytest.fixture
def mock_net2grid_config_flow(
    request: pytest.FixtureRequest,
) -> Generator[None, MagicMock, None]:
    """Return a mocked Net2Grid client."""
    with patch(
        "homeassistant.components.net2grid.config_flow.Net2Grid", autospec=True
    ) as net2grid_mock:
        net2grid = net2grid_mock.return_value
        net2grid.device.return_value = Net2GridDevice.from_dict(
            json.loads(load_fixture("device.json", DOMAIN))
        )
        yield net2grid


@pytest.fixture
def mock_net2grid():
    """Return a mocked Net2Grid client."""
    with patch(
        "homeassistant.components.net2grid.Net2Grid", autospec=True
    ) as net2grid_mock:
        net2grid = net2grid_mock.return_value
        net2grid.smartbridge = AsyncMock(
            return_value=SmartBridge.from_dict(
                json.loads(load_fixture("net2grid/smartbridge.json"))
            )
        )
        net2grid.device = AsyncMock(
            return_value=Net2GridDevice.from_dict(
                json.loads(load_fixture("net2grid/device.json"))
            )
        )
        yield net2grid_mock


@pytest.fixture
async def init_integration(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_net2grid: MagicMock
) -> MockConfigEntry:
    """Set up the Net2Grid integration for testing."""
    mock_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    return mock_config_entry
