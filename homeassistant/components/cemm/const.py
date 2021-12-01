"""Constants for the CEMM integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Final

DOMAIN: Final = "cemm"
LOGGER = logging.getLogger(__package__)
SCAN_INTERVAL = timedelta(seconds=5)

SERVICE_DEVICE: Final = "device"
SERVICE_SMARTMETER: Final = "smartmeter"

SERVICES: dict[str, str] = {
    SERVICE_DEVICE: "Device",
    SERVICE_SMARTMETER: "SmartMeter",
}
