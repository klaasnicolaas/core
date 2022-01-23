"""Support for Net2Grid sensors."""
from __future__ import annotations

from typing import Literal

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, ENERGY_KILO_WATT_HOUR, POWER_WATT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import Net2GridDataUpdateCoordinator
from .const import DOMAIN, SERVICE_SMARTBRIDGE, SERVICES

SENSORS: dict[Literal["smartbridge"], tuple[SensorEntityDescription, ...]] = {
    SERVICE_SMARTBRIDGE: (
        SensorEntityDescription(
            key="power_flow",
            name="Power Flow",
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        SensorEntityDescription(
            key="energy_consumption_total",
            name="Energy Consumption",
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        SensorEntityDescription(
            key="energy_production_total",
            name="Energy Production",
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
    ),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Net2Grid Sensors based on a config entry."""
    async_add_entities(
        Net2GridSensorEntity(
            coordinator=hass.data[DOMAIN][entry.entry_id],
            description=description,
            service_key=service_key,
            service=SERVICES[service_key],
        )
        for service_key, service_sensors in SENSORS.items()
        for description in service_sensors
    )


class Net2GridSensorEntity(CoordinatorEntity, SensorEntity):
    """Defines an Net2Grid sensor."""

    coordinator: Net2GridDataUpdateCoordinator

    def __init__(
        self,
        *,
        coordinator: Net2GridDataUpdateCoordinator,
        description: SensorEntityDescription,
        service_key: Literal["smartbridge"],
        service: str,
    ) -> None:
        """Initialize Net2Grid sensor."""
        super().__init__(coordinator=coordinator)
        self._service_key = service_key

        self.entity_id = f"{SENSOR_DOMAIN}.n2g_{description.key}"
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{service_key}_{description.key}"
        )

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={
                (DOMAIN, f"{coordinator.config_entry.entry_id}_{service_key}")
            },
            configuration_url=f"http://{coordinator.config_entry.data[CONF_HOST]}",
            sw_version=coordinator.data["device"].firmware,
            manufacturer=coordinator.data["device"].manufacturer,
            model=coordinator.data["device"].model,
            name=service,
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        value = getattr(
            self.coordinator.data[self._service_key], self.entity_description.key
        )
        return value
