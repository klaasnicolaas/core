"""Support for Autarco sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AutarcoData, AutarcoDataUpdateCoordinator
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

SENSORS_SOLAR: tuple[AutarcoSensorEntityDescription, ...] = (
    AutarcoSensorEntityDescription(
        key="power_production",
        name="Power Production",
        value_fn=lambda data: data.solar.power_production,
    ),
    AutarcoSensorEntityDescription(
        key="energy_production_today",
        name="Energy Production - Today",
        value_fn=lambda data: data.solar.energy_production_today,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Autarco sensors based on a config entry."""
    entities: list[AutarcoSensorEntity] = [
        AutarcoSensorEntity(
            coordinator=hass.data[DOMAIN][entry.entry_id],
            description=description,
        )
        for description in SENSORS_ACCOUNT
    ]

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
    ) -> None:
        """Initialize Autarco sensor."""
        super().__init__(coordinator=coordinator)

        self.entity_id = f"{SENSOR_DOMAIN}.{description.key}"
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.data.account.public_key}_{description.key}"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.data.account.public_key)},
            entry_type=DeviceEntryType.SERVICE,
            manufacturer="Autarco",
        )

    @property
    def native_value(self) -> int | float | str:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)
