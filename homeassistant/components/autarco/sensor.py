"""Support for Autarco sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ENERGY_KILO_WATT_HOUR,
    POWER_WATT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import AutarcoData, AutarcoDataUpdateCoordinator
from .const import DOMAIN


@dataclass
class AutarcoSensorEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[AutarcoData], float | int | str]


@dataclass
class AutarcoSensorEntityDescription(
    SensorEntityDescription, AutarcoSensorEntityDescriptionMixin
):
    """Sensor entity description."""


SENSORS_ACCOUNT: tuple[AutarcoSensorEntityDescription, ...] = (
    AutarcoSensorEntityDescription(
        key="name",
        name="Name",
        value_fn=lambda data: data.account.name,
    ),
    AutarcoSensorEntityDescription(
        key="city",
        name="City",
        value_fn=lambda data: data.account.city,
    ),
)

SENSORS_INVERTER: tuple[AutarcoSensorEntityDescription, ...] = (
    AutarcoSensorEntityDescription(
        key="serial_number",
        name="Serial number",
        value_fn=lambda inverters: inverters.values(),
    ),
    AutarcoSensorEntityDescription(
        key="out_ac_power",
        name="AC output power",
        value_fn=lambda inverters: inverters.values(),
    ),
)

SENSORS_SOLAR: tuple[AutarcoSensorEntityDescription, ...] = (
    AutarcoSensorEntityDescription(
        key="power_production",
        name="Power Production",
        native_unit_of_measurement=POWER_WATT,
        device_class=SensorDeviceClass.POWER,
        value_fn=lambda data: data.solar.power_production,
    ),
    AutarcoSensorEntityDescription(
        key="energy_production_today",
        name="Energy Production - Today",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        value_fn=lambda data: data.solar.energy_production_today,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Autarco sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[AutarcoSensorEntity] = []
    for index, inverter in enumerate(coordinator.data.inverters, start=1):
        entities.extend(
            AutarcoSensorEntity(
                coordinator=coordinator,
                description=description,
                name=f"Inverter - {inverter.serial_number}",
                service=f"inverter_{index}",
            )
            for description in SENSORS_INVERTER
        )
    entities.extend(
        AutarcoSensorEntity(
            coordinator=coordinator,
            description=description,
            name="Account",
            service="account",
        )
        for description in SENSORS_ACCOUNT
    )
    entities.extend(
        AutarcoSensorEntity(
            coordinator=coordinator,
            description=description,
            name="Solar",
            service="solar",
        )
        for description in SENSORS_SOLAR
    )
    print(hass.data[DOMAIN][entry.entry_id].data)
    async_add_entities(entities)


class AutarcoSensorEntity(CoordinatorEntity[AutarcoData], SensorEntity):
    """Defines an Autarco sensor."""

    coordinator: AutarcoDataUpdateCoordinator
    entity_description: AutarcoSensorEntityDescription

    def __init__(
        self,
        *,
        coordinator: AutarcoDataUpdateCoordinator,
        description: AutarcoSensorEntityDescription,
        name: str,
        service: str,
    ) -> None:
        """Initialize Autarco sensor."""
        super().__init__(coordinator=coordinator)

        self.entity_description = description
        self.entity_id = f"{SENSOR_DOMAIN}.{service}_{description.key}"
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{service}_{description.key}"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{coordinator.config_entry.entry_id}_{service}")},
            entry_type=DeviceEntryType.SERVICE,
            manufacturer="Autarco",
            name=name,
        )

    @property
    def native_value(self) -> int | float | str:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)
