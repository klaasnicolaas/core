"""Test the Net2Grid config flow."""
from unittest.mock import MagicMock

from net2grid import Net2GridConnectionError

from homeassistant.components import zeroconf
from homeassistant.components.net2grid.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER, SOURCE_ZEROCONF
from homeassistant.const import CONF_HOST, CONF_MAC, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import (
    RESULT_TYPE_ABORT,
    RESULT_TYPE_CREATE_ENTRY,
    RESULT_TYPE_FORM,
)


async def test_full_user_flow_implementation(
    hass: HomeAssistant, mock_net2grid_config_flow: MagicMock, mock_setup_entry: None
) -> None:
    """Test the full manual user flow from start to finish."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_USER},
    )

    assert result.get("step_id") == SOURCE_USER
    assert result.get("type") == RESULT_TYPE_FORM
    assert "flow_id" in result

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_HOST: "192.168.1.123"}
    )

    assert result.get("title") == "test home"
    assert result.get("type") == RESULT_TYPE_CREATE_ENTRY
    assert "data" in result
    assert result["data"][CONF_HOST] == "192.168.1.123"
    assert "result" in result
    assert result["result"].unique_id == "aabbccddeeff"


async def test_full_zeroconf_flow_implementationn(
    hass: HomeAssistant, mock_net2grid_config_flow: MagicMock, mock_setup_entry: None
) -> None:
    """Test the full manual user flow from start to finish."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=zeroconf.ZeroconfServiceInfo(
            host="192.168.1.123",
            hostname="example.local.",
            name="mock_name",
            port=None,
            properties={CONF_MAC: "aabbccddeeff"},
            type="mock_type",
        ),
    )

    assert result.get("description_placeholders") == {CONF_NAME: "Net2Grid"}
    assert result.get("step_id") == "zeroconf_confirm"
    assert result.get("type") == RESULT_TYPE_FORM
    assert "flow_id" in result

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={}
    )

    assert result2.get("title") == "test home"
    assert result2.get("type") == RESULT_TYPE_CREATE_ENTRY

    assert "data" in result2
    assert result2["data"][CONF_HOST] == "192.168.1.123"
    assert "result" in result2
    assert result2["result"].unique_id == "aabbccddeeff"


async def test_connection_error(
    hass: HomeAssistant, mock_net2grid_config_flow: MagicMock
) -> None:
    """Test we show user form on Net2Grid connection error."""
    mock_net2grid_config_flow.device.side_effect = Net2GridConnectionError
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_USER},
        data={CONF_HOST: "example.com"},
    )

    assert result.get("type") == RESULT_TYPE_FORM
    assert result.get("step_id") == "user"
    assert result.get("errors") == {"base": "cannot_connect"}


async def test_zeroconf_connection_error(
    hass: HomeAssistant, mock_net2grid_config_flow: MagicMock
) -> None:
    """Test we abort zeroconf flow on Net2Grid connection error."""
    mock_net2grid_config_flow.device.side_effect = Net2GridConnectionError

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=zeroconf.ZeroconfServiceInfo(
            host="192.168.1.123",
            hostname="example.local.",
            name="mock_name",
            port=None,
            properties={CONF_MAC: "aabbccddeeff"},
            type="mock_type",
        ),
    )

    assert result.get("type") == RESULT_TYPE_ABORT
    assert result.get("reason") == "cannot_connect"
