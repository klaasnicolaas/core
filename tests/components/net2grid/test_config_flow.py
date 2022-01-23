"""Test the Net2Grid config flow."""
from unittest.mock import MagicMock

from net2grid import Net2GridConnectionError

from homeassistant.components import zeroconf
from homeassistant.components.net2grid.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import RESULT_TYPE_CREATE_ENTRY, RESULT_TYPE_FORM


async def test_full_user_flow_implementation(
    hass: HomeAssistant, mock_net2grid_config_flow: MagicMock, mock_setup_entry: None
) -> None:
    """Test the full manual user flow from start to finish."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_USER},
    )

    assert result.get("step_id") == "user"
    assert result.get("type") == RESULT_TYPE_FORM
    assert "flow_id" in result

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_HOST: "192.168.1.123"}
    )

    assert result.get("title") == "WLED RGB Light"
    assert result.get("type") == RESULT_TYPE_CREATE_ENTRY
    assert "data" in result
    assert result["data"][CONF_HOST] == "192.168.1.123"
    assert "result" in result
    assert result["result"].unique_id == "unique_thingy"
