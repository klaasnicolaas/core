"""Constants for the CEMM integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Final

DOMAIN: Final = "cemm"
LOGGER = logging.getLogger(__package__)
SCAN_INTERVAL = timedelta(seconds=5)

CONF_CONNECTIONS: Final = "connections"

SERVICE_DEVICE: Final = "device"
SERVICE_SMARTMETER: Final = "smartmeter"
SERVICE_SOLARPANELS: Final = "solarpanels"

SERVICES: dict[str, str] = {
    SERVICE_SMARTMETER: "SmartMeter",
    SERVICE_SOLARPANELS: "SolarPanels",
}
