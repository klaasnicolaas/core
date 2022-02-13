"""Tests for the sensors provided by the Net2Grid integration."""
from unittest.mock import MagicMock, patch

from homeassistant.components.net2grid.const import DOMAIN
from homeassistant.components.sensor import (
    ATTR_STATE_CLASS,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_FRIENDLY_NAME,
    ATTR_ICON,
    ATTR_UNIT_OF_MEASUREMENT,
    ENERGY_KILO_WATT_HOUR,
    POWER_WATT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from tests.common import MockConfigEntry


async def test_sensors(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_net2grid: MagicMock,
) -> None:
    """Test the Net2Grid - SmartBridge sensors."""
    entry_id = init_integration.entry_id
    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)

    state = hass.states.get("sensor.n2g_energy_consumption_total")
    entry = entity_registry.async_get("sensor.n2g_energy_consumption_total")
    assert entry
    assert state
    assert entry.unique_id == f"{entry_id}_smartbridge_energy_consumption_total"
    assert state.state == "17762.1"
    assert state.attributes.get(ATTR_FRIENDLY_NAME) == "Energy Consumption"
    assert state.attributes.get(ATTR_STATE_CLASS) == SensorStateClass.TOTAL_INCREASING
    assert state.attributes.get(ATTR_UNIT_OF_MEASUREMENT) == ENERGY_KILO_WATT_HOUR
    assert state.attributes.get(ATTR_DEVICE_CLASS) == SensorDeviceClass.ENERGY
    assert ATTR_ICON not in state.attributes

    state = hass.states.get("sensor.n2g_energy_production_total")
    entry = entity_registry.async_get("sensor.n2g_energy_production_total")
    assert entry
    assert state
    assert entry.unique_id == f"{entry_id}_smartbridge_energy_production_total"
    assert state.state == "21214.6"
    assert state.attributes.get(ATTR_FRIENDLY_NAME) == "Energy Production"
    assert state.attributes.get(ATTR_STATE_CLASS) == SensorStateClass.TOTAL_INCREASING
    assert state.attributes.get(ATTR_UNIT_OF_MEASUREMENT) == ENERGY_KILO_WATT_HOUR
    assert state.attributes.get(ATTR_DEVICE_CLASS) == SensorDeviceClass.ENERGY
    assert ATTR_ICON not in state.attributes

    state = hass.states.get("sensor.n2g_power_flow")
    entry = entity_registry.async_get("sensor.n2g_power_flow")
    assert entry
    assert state
    assert entry.unique_id == f"{entry_id}_smartbridge_power_flow"
    assert state.state == "338"
    assert state.attributes.get(ATTR_FRIENDLY_NAME) == "Power Flow"
    assert state.attributes.get(ATTR_STATE_CLASS) == SensorStateClass.MEASUREMENT
    assert state.attributes.get(ATTR_UNIT_OF_MEASUREMENT) == POWER_WATT
    assert state.attributes.get(ATTR_DEVICE_CLASS) == SensorDeviceClass.POWER
    assert ATTR_ICON not in state.attributes

    assert entry.device_id
    device_entry = device_registry.async_get(entry.device_id)
    assert device_entry
    assert device_entry.identifiers == {(DOMAIN, f"{entry_id}_smartbridge")}
    assert device_entry.name == "SmartBridge"
    assert device_entry.manufacturer == "NET2GRID"
    assert device_entry.entry_type is dr.DeviceEntryType.SERVICE
    assert device_entry.model == "SBWF3102"
    assert device_entry.sw_version == "1.6.16"
