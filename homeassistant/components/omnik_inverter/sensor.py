"""Support for Omnik Inverter sensors."""
from __future__ import annotations

from typing import Literal

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_IDENTIFIERS,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_NAME,
    ATTR_SW_VERSION,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    ENERGY_KILO_WATT_HOUR,
    POWER_WATT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import OmnikInverterDataUpdateCoordinator
from .const import (
    ATTR_ENTRY_TYPE,
    DOMAIN,
    ENTRY_TYPE_SERVICE,
    SERVICE_INVERTER,
    SERVICES,
)

SENSORS: dict[Literal["inverter"], tuple[SensorEntityDescription, ...]] = {
    SERVICE_INVERTER: (
        SensorEntityDescription(
            key="solar_current_power",
            name="Current Power Production",
            icon="mdi:weather-sunny",
            native_unit_of_measurement=POWER_WATT,
            device_class=DEVICE_CLASS_POWER,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
        SensorEntityDescription(
            key="solar_energy_today",
            name="Solar Production - Today",
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=DEVICE_CLASS_ENERGY,
            state_class=STATE_CLASS_TOTAL_INCREASING,
        ),
        SensorEntityDescription(
            key="solar_energy_total",
            name="Solar Production - Total",
            icon="mdi:chart-line",
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=DEVICE_CLASS_ENERGY,
            state_class=STATE_CLASS_TOTAL_INCREASING,
        ),
    ),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Omnik Inverter Sensors based on a config entry."""
    async_add_entities(
        OmnikInverterSensorEntity(
            coordinator=hass.data[DOMAIN][entry.entry_id],
            description=description,
            service_key=service_key,
            name=entry.title,
            service=SERVICES[service_key],
        )
        for service_key, service_sensors in SENSORS.items()
        for description in service_sensors
    )


class OmnikInverterSensorEntity(CoordinatorEntity, SensorEntity):
    """Defines an Omnik Inverter sensor."""

    coordinater: OmnikInverterDataUpdateCoordinator

    def __init__(
        self,
        *,
        coordinator: OmnikInverterDataUpdateCoordinator,
        description: SensorEntityDescription,
        service_key: Literal["inverter"],
        name: str,
        service: str,
    ) -> None:
        """Initialize Omnik Inverter sensor."""
        super().__init__(coordinator=coordinator)
        self._service_key = service_key

        self.entity_id = f"{SENSOR_DOMAIN}.{name}_{description.key}"
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{service_key}_{description.key}"
        )

        self._attr_device_info = {
            ATTR_IDENTIFIERS: {
                (DOMAIN, f"{coordinator.config_entry.entry_id}_{service_key}")
            },
            ATTR_NAME: service,
            ATTR_MANUFACTURER: "Omnik",
            ATTR_MODEL: coordinator.data["inverter"].model,
            ATTR_SW_VERSION: coordinator.data["inverter"].firmware_main,
            ATTR_ENTRY_TYPE: ENTRY_TYPE_SERVICE,
        }

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        value = getattr(
            self.coordinator.data[self._service_key], self.entity_description.key
        )
        if isinstance(value, str):
            return value.lower()
        return value
